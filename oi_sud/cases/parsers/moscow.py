import dateparser
import re
import time
import traceback
import pprint
import requests
from bs4 import BeautifulSoup
from dateparser.conf import settings as dateparse_settings
from django.utils.html import strip_tags
from django.utils.timezone import get_current_timezone, localtime

from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.cases.parsers.main import CourtSiteParser
from oi_sud.core.utils import get_query_key
from oi_sud.core.textract import DocParser, DocXParser
from oi_sud.cases.utils import normalize_name
from oi_sud.courts.models import Court, Judge
from oi_sud.cases.consts import site_types_by_codex, EVENT_TYPES, EVENT_RESULT_TYPES, RESULT_TYPES, APPEAL_RESULT_TYPES, instances_dict, moscow_params_dict
from oi_sud.cases.models import Case, Defendant
from dateutil.relativedelta import relativedelta

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False

event_types_dict = {y: x for x, y in dict(EVENT_TYPES).items()}
event_result_types_dict = {y: x for x, y in dict(EVENT_RESULT_TYPES).items()}
result_types_dict = {y: x for x, y in dict(RESULT_TYPES).items()}
appeal_result_types_dict = {y: x for x, y in dict(APPEAL_RESULT_TYPES).items()}

from pytz import timezone, utc


class MoscowParser(CourtSiteParser):



    def get_court_from_url(self, url):
        # получаем суд из урла карточки

        url = url.split('/services')[0]
        print(url, 'URL')
        court = Court.objects.filter(url=url).first()
        print(court, 'court')
        return court


    def get_pages_number(self, page):
        # получаем число страниц с делами

        last_page_a = page.find('a', class_="intheend")
        if last_page_a:
            last_page_href = last_page_a['href']
            pages_number = int(get_query_key(last_page_href, 'page'))
            return pages_number
        else:
            return 1

    def get_cases_urls_from_list(self, page):
        # получаем урлы карточек дел из страницы поиска
        urls = []
        events = page.tbody.findAll('tr')
        for ev in events:
            ev_cols = ev.findAll('td')
            href = 'https://mos-gorsud.ru'+ev_cols[0]('a')[0]['href']
            if Case.objects.filter(url=href).exists():
                continue
            urls.append(href)

        return urls

    def get_all_cases_urls(self, limit_pages=False):
        # Получаем все урлы дел по данной статье
        print('get all urls')
        txt, status_code = self.send_get_request(self.url)
        if status_code != 200:
            print("GET error: ", status_code)
            print('Unable to save cases')
            return None
        first_page = BeautifulSoup(txt, 'html.parser')
        pages_number = self.get_pages_number(first_page)  # TODO CHANGE
        print(pages_number,'pages_number')
        if pages_number > 3 and limit_pages:
            pages_number = 3 #FOR TESTING
        all_pages = [first_page, ]

        if pages_number != 1:

            pages_urls = [f'{self.url}&page={p}' for p in range(2, pages_number + 1)]

            for url in pages_urls:
                txt, status_code = self.send_get_request(url)
                if status_code != 200:
                    print("GET error: ", status_code)
                    continue
                page = BeautifulSoup(txt, 'html.parser')
                all_pages.append(page)

        all_cases_urls = []

        for page in all_pages:
            try:
                urls = self.get_cases_urls_from_list(page)
                all_cases_urls += urls
            except AttributeError:
                print('error')

        if all_cases_urls == []:
            print('...Got no cases urls')
        else:
            print('...Got all cases urls')

        return all_cases_urls

    def url_to_str(self, url):
        ''' выгружает текст из файла doc / docx, загружаемого по ссылке'''
        file_res, status, content, extension = self.send_get_request(url, extended=True)
        bytes0 = content#file_res#[2]
        exten = extension
        filename = "txt." + exten
        f = open(filename, 'wb')
        f.write(bytes0)
        f.close()
        try:
            if exten == 'doc':
                return DocParser().process(filename, 'utf-8')
            elif exten == 'docx':
                return DocXParser().process(filename, 'utf-8')
        except:
            return ''


    def get_raw_case_information(self, url):

        # парсим карточку дела

        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            print("GET error: ", status_code)
            return
        page = BeautifulSoup(txt, 'html.parser')

        case_info = {}

        case_info['court'] = self.get_court_from_url(url)
        case_info['url'] = url

        # выгружаем информацию из центральной таблицы на странице

        content_dict = {}
        content = page.findAll('div', class_="row_card")

        results_dict = {'Вступило в силу':'Вынесено постановление о назначении административного наказания',
                        'Обжаловано':'Вынесено постановление о назначении административного наказания'}

        # добавляем каждую строку в словарь
        for row in content:
            row_left = row.find('div', class_='left')
            left = row_left.string.strip()
            row_right = row.find('div', class_='right')
            right = row_right.text.strip()
            content_dict[left] = right

        # записываем данные из первой таблицы в финальный словарь

        # словарь с названиями параметров, которые мы будем записывать в финальный словарь
        dict_names = {'Номер дела': 'case_number', 'Уникальный идентификатор дела': 'case_uid',
                      'Дата регистрации': 'entry_date', 'Cудья': 'judge',
                      'Привлекаемое лицо': 'defendant', 'Статья КоАП РФ': 'codex_articles','Текущее состояние':'result_type'}
        defense = {}
        for key in content_dict.keys():
            if key in dict_names.keys():

                # закидываем привлекаемое лицо и статью во внутренний список словарей
                if key in ['Привлекаемое лицо', 'Статья КоАП РФ']:
                    defense[dict_names[key]] = content_dict[key]

                # разбиваем "Текущее сосотояние" на тип и дату
                elif key == 'Текущее состояние':
                    # проверяем, есть ли тип и дата, если только тип, оставляем дату пустой строкой
                    if ', ' in content_dict['Текущее состояние']:
                        result_type, result_date = content_dict['Текущее состояние'].split(', ')
                    else:
                        result_type, result_date = content_dict['Текущее состояние'], ''
                    # записываем тип и дату в финальный словарь
                    case_info['result_type'], case_info['result_date'] = result_type, result_date
                    if case_info['result_type'] in results_dict:
                        case_info['result_type'] = results_dict[case_info['result_type']]

                else:
                    case_info[dict_names[key]] = content_dict[key]
            else:
                print ('не вошло в финальный словарь:', key,  content_dict[key])
        case_info['defenses'] = [defense]

        # выгружаем данные из таблиц "судебные заседания" и "судебные акты"
        table = page.findAll('table', class_="custom_table mainTable")

        table_sessions = None
        table_acts = None

        div_sessions = page.find('div', id='sessions')
        if div_sessions:
            table_sessions = div_sessions.find('table')

        div_acts = page.find('div', id='act-documents')
        if div_acts:
            table_acts = div_acts.find('table')

        # выгружаем информацию о судебных заседаниях по делу
        events = []

        if table_sessions:
            # какие параметры нам нужны, их имена на сайте и в итоговом словаре
            event_names = {'Стадия': 'type', 'date': 'date', 'time': 'time', 'courtroom': 'courtroom',
                           'Результат': 'result', 'Основание': 'reason'}
            # выгружаем таблицу с прошедшими заседаниями (центральная нижняя)
            heads = [head.string.strip() for head in table[0].findAll('th')]
            results = [result.string.strip() for result in table[0].findAll('td')]

            num = len(results) // len(heads)
            for i in range(num):
                event = dict(zip(heads, results[(i * len(heads)):((i + 1) * len(heads))]))

                # разбиваем дату и время на дату и время
                if 'Дата и время' in event.keys():
                    date, time = event['Дата и время'].split(' ')
                    event['date'] = date
                    event['time'] = time

                # убираем лишние слова из "зала"
                if 'Зал' in event.keys():
                    if ' - ' in event['Зал']:
                        courtroom = event['Зал'].split(' - ')[0]
                    else:
                        courtroom = event['Зал']
                    event['courtroom'] = courtroom

                # оставляем нужные нам параметры, меняем имена
                event_fin = {}
                for key in event_names.keys():
                    if key in event.keys():
                        event_fin[event_names[key]] = event[key]

                # добавляем строку события в итоговыйсписок словарей
                events.append(event_fin)
        case_info['events'] = events

        # ищем ссылку на текст решения
        links = []
        decision_urls = []

        if table_acts:
            links = ['https://www.mos-gorsud.ru' + x['href'] for x in table_acts.findAll('a')]
            if len(links):
                text = self.url_to_str(links[0])
                case_info['result_text'] = text

        return case_info


    def get_result_text_url(self, page):
        # return url
        raise NotImplementedError

    def get_result_text(self, url):
        # return text
        raise NotImplementedError


    def get_koap_article(self, raw_string):
        # получаем объекты статей КОАП из строки, полученной из карточки дела

        m = re.search(r'Ст\.\s([0-9\.]+),?\s?Ч?\.?([0-9\.]*)', raw_string)

        if m:
            article = m.group(1)
            part = m.group(2)
            if part == '':
                part = None
            codex_article = CodexArticle.objects.filter(codex='koap', article_number=article, part=part).first()
            if codex_article:
                return [codex_article]
        return []

    def get_uk_articles(self, raw_string):
        # получаем объекты статей УК из строки, полученной из карточки дела
        raise NotImplementedError


class MoscowCasesGetter(CommonParser):


    @staticmethod
    def generate_params(string, params):

        result_string = ''
        result_string += string
        for k, v in params.items():
            if k in moscow_params_dict:
                result_string += '&{0}={1}'.format(moscow_params_dict[k], v)
        return result_string

    def get_cases(self, instance, codex, entry_date_from=None, articles_list=None):
        # получаем дела по инстанции, типу производства
        processType = '3' if codex == 'koap' else '6'  # 3 for koap, 6 for uk

        if articles_list:
            articles = CodexArticle.objects.get_from_list(articles_list, codex=codex)
        else:
            articles = CodexArticle.objects.filter(codex=codex)

        for article in articles:
            if article.part:
                article_string = f'Ст.%20{article.article_number},%20Ч.{article.part}'
            else:
                article_string = f'Ст.%20{article.article_number}'
            params = {'articles': article_string, 'instance': instance, 'processType': processType}
            if entry_date_from:
                params['entry_date_from'] = entry_date_from  # DD.MM.YYYY
            url = self.generate_params('https://mos-gorsud.ru/mgs/search?courtAlias=', params)
            print(url)

            MoscowParser(url=url, stage=instance, codex=codex).save_cases()