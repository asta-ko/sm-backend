# coding=utf-8
import re

from bs4 import BeautifulSoup
from dateparser.conf import settings as dateparse_settings
from django.utils.timezone import get_current_timezone
from oi_sud.cases.consts import moscow_params_dict
from oi_sud.cases.models import Case
from oi_sud.cases.parsers.main import CourtSiteParser
from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.core.textract import DocParser, DocXParser
from oi_sud.core.utils import get_query_key
from oi_sud.courts.models import Court

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False


class MoscowParser(CourtSiteParser):

    def get_article_string(self):

        if not self.article:
            print('no self article')
            return None

        koap_uk_space = ''
        if self.article.codex == 'uk':
            koap_uk_space = ' '

        if self.article.part:
            article_string = f'Ст. {self.article.article_number}, Ч.{koap_uk_space}{self.article.part}'
        else:
            article_string = f'Ст. {self.article.article_number}'
        return article_string

    def get_court_from_url(self, url):
        # получаем суд из урла карточки

        url = url.split('/services')[0]
        court = Court.objects.filter(url=url).first()
        if not court:
            court = Court.objects.filter(region=77, type=2).first()  # мосгорсуд
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
            href = 'https://mos-gorsud.ru' + ev_cols[0]('a')[0]['href']
            # проверка на точное соотстветствие, иначе смешает, например, ч.6 и ч.6.1
            if ev_cols[4].text.strip() != self.get_article_string():
                print('article string went wrong')
                continue

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
        print(pages_number, 'pages_number')
        if pages_number > 3 and limit_pages:
            pages_number = 3  # FOR TESTING
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

        if not all_cases_urls:
            print('...Got no cases urls')
        else:
            print('...Got all cases urls')

        return all_cases_urls

    def try_to_parse_result_text(self, parser, filename):
        try:
            text = parser.process(filename, 'utf-8')
            return text
        except Exception as e:
            print('could not process')
            return ''

    def url_to_str(self, url):
        """ выгружает текст из файла doc / docx, загружаемого по ссылке """
        file_res, status, content, extension = self.send_get_request(url, extended=True)
        if not extension:
            extension = 'docx'
        bytes0 = content  # file_res#[2]
        filename = "txt." + extension
        f = open(filename, 'wb')
        f.write(bytes0)
        f.close()

        if extension == 'docx':
            return self.try_to_parse_result_text(DocXParser(), filename)
        elif extension == 'doc':
            return self.try_to_parse_result_text(DocParser(), filename)
        elif not extension:
            docx = self.try_to_parse_result_text(DocXParser(), filename)
            if not docx:
                return self.try_to_parse_result_text(DocParser(), filename)

    def get_raw_case_information(self, url):

        # парсим карточку дела

        print(url, 'case url')

        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            print("GET error: ", status_code)
            return
        page = BeautifulSoup(txt, 'html.parser')

        case_info = {'court': self.get_court_from_url(url), 'url': url.split('?')[0]}

        content_dict = {}
        content = page.findAll('div', class_="row_card")

        # добавляем каждую строку в словарь
        for row in content:
            row_left = row.find('div', class_='left')
            left = row_left.string.strip()
            row_right = row.find('div', class_='right')
            right = row_right.text.strip()

            if 'Номер дела в суде вышестоящей инстанции' in left or 'Номер дела в суде нижестоящей инстанции' in left:

                links = row_right.findAll('a')
                if len(links):
                    hrefs = ['https://mos-gorsud.ru' + x['href'] for x in links]
                    nums = [x.text for x in links]
                    content_dict['Ссылка на связанное дело'] = hrefs

                else:
                    nums = [x.strip() for x in row_right.text.strip().split(',')]
                content_dict[left] = nums
            else:
                content_dict[left] = right

        # записываем данные из первой таблицы в финальный словарь

        # словарь с названиями параметров, которые мы будем записывать в финальный словарь
        dict_names = {
            'Номер дела': 'case_number', 'Уникальный идентификатор дела': 'case_uid',
            'Дата регистрации': 'entry_date',
            'Дата поступления': 'entry_date',
            'Дата поступления дела в апелляционную инстанцию': 'entry_date',
            'Дата вступления в силу': 'result_valid_date',
            'Дата вступления решения в силу': 'result_valid_date',
            'Номер дела ~ материала': 'case_number',
            'Cудья': 'judge',
            'Привлекаемое лицо': 'defendant', 'Статья КоАП РФ': 'codex_articles',
            # 'Текущее состояние': 'current_state',
            'Дата рассмотрения дела в первой инстанции': 'result_date',
            'Дата окончания': 'result_date',
            'Номер дела в суде вышестоящей инстанции': 'linked_case_number',
            'Номер дела в суде нижестоящей инстанции': 'linked_case_number',
            'Ссылка на связанное дело': 'linked_case_url',
            'Осужденный (оправданный, обвиняемый)': 'uk_defense',
            'Лицо': 'uk_defense',
            'Подсудимый': 'uk_defense'
            }
        defense = {}
        for key in content_dict.keys():
            if key in dict_names.keys():
                # закидываем привлекаемое лицо и статью во внутренний список словарей
                if key in ['Привлекаемое лицо', 'Статья КоАП РФ']:
                    defense[dict_names[key]] = content_dict[key]
                    case_info['defenses'] = [defense]

                elif key in ['Осужденный (оправданный, обвиняемый)', 'Подсудимый', 'Лицо']:
                    case_info['defenses'] = self.get_uk_defenses(content_dict[key])

                else:
                    case_info[dict_names[key]] = content_dict[key]
            else:
                print('не вошло в финальный словарь:', key, content_dict[key])

        # выгружаем данные из таблиц "судебные заседания" и "судебные акты"
        table = page.findAll('table', class_="custom_table mainTable")

        table_sessions = None
        table_acts = None
        table_states = None
        # table_case_location = None

        div_sessions = page.find('div', id='sessions')
        if div_sessions:
            table_sessions = div_sessions.find('table')

        div_acts = page.find('div', id='act-documents')
        if div_acts:
            table_acts = div_acts.find('table')

        div_states = page.find('div', id='state-history')
        if div_states:
            states_tables = div_states.findAll('table')
            if len(states_tables) > 0:
                table_states = states_tables[0]
            # if len(states_tables) > 1:
            # table_case_location = states_tables[1] #TODO: где находится дело (скорее не нужно)

        # выгружаем информацию о судебных заседаниях по делу
        events = []

        if table_sessions:
            # какие параметры нам нужны, их имена на сайте и в итоговом словаре
            event_names = {
                'Стадия': 'type', 'date': 'date', 'time': 'time', 'courtroom': 'courtroom',
                'Результат': 'result', 'Основание': 'reason'
                }
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

        if table_states:
            for tr in table_states.findAll('tr'):

                tds = tr.findAll('td')

                if len(tds) > 1:
                    if tds[1] == 'Рассмотрение':
                        continue

                    if tds[0].text.strip() and tds[1].text.strip():
                        events.append({'type': tds[1].text.strip(), 'date': tds[0].text.strip()})

        # if table_case_location:  TODO: ДАТЫ
        #     for tr in table_case_location.findAll('tr'):
        #         tds = tr.findAll('td')
        #         if len(tds) > 1 and 'Направлено в апелляционную инстанцию' in tds[1].text:
        #             case_info['forwarding_to_higher_court_date'] = tds[0]
        #
        # if table_acts:
        #     trs = table_acts.findAll('tr')
        #     for tr in trs:
        #         tds = tr.findAll('td')
        #         if len(tds) > 1 and 'Решение по жалобе' in tds[1].text:
        #             case_info['appeal_date'] = tds[0]

        case_info['events'] = events

        # ищем ссылку на текст решения

        if table_acts:
            trs = table_acts.findAll('tr')
            for tr in trs:
                tds = tr.findAll('td')
                if len(tds) > 1 and any(element in tds[1].text for element in
                                        ['Приговор', 'Решение по жалобе', 'Постановление',
                                         'Определение о возвращении']):
                    if tds[2].find('a'):
                        link = 'https://www.mos-gorsud.ru' + tds[2].find('a')['href']
                        text = self.url_to_str(link)
                        case_info['result_text'] = text

        return case_info

    def get_uk_defenses(self, defenses_string):

        defenses = []
        defenses_arr = re.split(r',(?= \w+ \w\.\w\.)', defenses_string)
        for d in defenses_arr:
            d = re.sub('\(отм\. \d{2}\.\d{2}\.\d{4}\) ', '', d)
            defendant = d.split('(')[0].strip()
            articles_str = ''
            if len(d.split('(')) > 1:
                articles_str = d.split('(')[1].strip(')')
            defense = {'defendant': defendant, 'codex_articles': articles_str}
            defenses.append(defense)
        return defenses

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

        codex_articles = []
        arr = raw_string.split('; ')
        for item in arr:

            item = item.strip()
            m = re.search(r'Ст\. ([[0-9\.]+)\s?,?\s?Ч?\.?\s?([0-9\.]*)', item)
            if m:
                article = m.group(1)
                part = m.group(2)
                if part == '':
                    part = None
                codex_article = CodexArticle.objects.filter(codex='uk', article_number=article,
                                                            part=part).first()
                if codex_article:
                    codex_articles.append(codex_article)
        return codex_articles


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
        process_type = '3' if codex == 'koap' else '6'  # 3 for koap, 6 for uk

        if articles_list:
            articles = CodexArticle.objects.get_from_list(articles_list, codex=codex)
        else:
            articles = CodexArticle.objects.filter(codex=codex, active=True)

        koap_uk_space = ''
        if codex == 'uk':
            koap_uk_space = '%20'
        for article in articles:
            if article.part:
                article_string = f'Ст.%20{article.article_number},%20Ч.{koap_uk_space}{article.part}'
            else:
                article_string = f'Ст.%20{article.article_number}'
            params = {'articles': article_string, 'instance': instance, 'processType': process_type}
            if entry_date_from:
                params['entry_date_from'] = entry_date_from  # DD.MM.YYYY
            url = self.generate_params('https://mos-gorsud.ru/mgs/search?courtAlias=', params)
            print(url)

            MoscowParser(url=url, stage=instance, codex=codex, article=article).save_cases()
