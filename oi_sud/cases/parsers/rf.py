import traceback
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

import time
import re
from dateparser.conf import settings as dateparse_settings
from django.utils.html import strip_tags
from django.utils.timezone import get_current_timezone

from oi_sud.cases.consts import site_types_by_codex, EVENT_TYPES, EVENT_RESULT_TYPES, RESULT_TYPES, APPEAL_RESULT_TYPES, \
    instances_dict
from oi_sud.cases.models import Case
from oi_sud.cases.parsers.main import CourtSiteParser
from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.core.utils import get_query_key
from oi_sud.courts.models import Court

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False

event_types_dict = {y: x for x, y in dict(EVENT_TYPES).items()}
event_result_types_dict = {y: x for x, y in dict(EVENT_RESULT_TYPES).items()}
result_types_dict = {y: x for x, y in dict(RESULT_TYPES).items()}
appeal_result_types_dict = {y: x for x, y in dict(APPEAL_RESULT_TYPES).items()}


class RFCourtSiteParser(CourtSiteParser):
    def get_koap_article(self, raw_string):
        # получаем объекты статей КОАП из строки, полученной из карточки дела

        m = re.search(r'КоАП:\sст\.\s([0-9\.]+)\s?ч?\.?([0-9\.]*)', raw_string)

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
        raw_list = list(set(raw_string.replace('УК РФ', '').split(';')))
        codex_articles = []
        for item in raw_list:
            codex_article = None
            item = item.strip()
            m = re.search(r'ст\.([0-9\.]+)\s?ч?\.?([0-9\.]*)', item)
            if m:
                article = m.group(1)
                part = m.group(2)
                if part == '':
                    part = None
                codex_article = CodexArticle.objects.filter(codex='uk', article_number=article, part=part).first()
            if codex_article:
                codex_articles.append(codex_article)
        return codex_articles

    def parse_defenses(self, el):
        # Получаем имя обвиняемого и статьи (может быть несколько)
        defenses = []
        title_tr = None
        title_tr_index = None
        title_tds = []
        defendant_index = None
        codex_articles_index = None
        trs = el.findAll('tr')
        for index, tr in enumerate(trs):

            tr_text = tr.text

            if 'ФИО' in tr_text or 'Фамилия' in tr_text or 'статей' in tr_text:
                title_tr = tr
                title_tr_index = index

        if not title_tr:
            title_tds = el.findAll('td', attrs={'align': 'center'})
            if not title_tds:
                title_tds = el.findAll('td', attrs={'style': 'text-align:center;'})
            title_tr_index = 2
        else:
            title_tds = title_tr.findAll('td')

        for index, td in enumerate(title_tds):
            td_text = td.text
            if 'ФИО' in td_text or 'Фамилия' in td_text:
                defendant_index = index
            if 'статей' in td_text:
                codex_articles_index = index

        for tr in trs[title_tr_index:]:
            if 'ФИО' in tr.text or 'статей' in tr.text or 'Фамилия' in tr.text or 'Информация скрыта' in tr.text:
                continue
            tds = tr.findAll('td')
            if len(tds) >= defendant_index and len(tds) >= codex_articles_index:
                defendant = tds[defendant_index].text.strip()
                codex_articles = tds[codex_articles_index].text.strip()
                print(defendant, codex_articles)
                defenses.append({'defendant': defendant, 'codex_articles': codex_articles})

        return defenses



class FirstParser(RFCourtSiteParser):

    # в системе судрф есть 2 типа сайтов судов, здесь мы обрабатываем первый (как https://krv--spb.sudrf.ru)

    def get_pages_number(self, page):
        # получаем число страниц с делами
        pagination_a = page.find('a', attrs={'title': 'На последнюю страницу списка'})
        if not pagination_a:
            return 1
        else:
            last_page_href = pagination_a['href']
            pages_number = int(get_query_key(last_page_href, 'page'))
            return pages_number

    def get_cases_urls_from_list(self, page):
        # получаем урлы карточек дел из страницы поиска
        urls = []
        tds = page.find('table', id='tablcont').findAll('td', attrs={
            'title': 'Для получения справки по делу, нажмите на номер дела'})
        for td in tds:
            href = td.find('a')['href']
            if Case.objects.filter(url=href).exists():
                continue
            urls.append(href + '&nc=1')
        return urls

    def get_result_text_url(self, page):
        # получаем урл на текст решения
        ths = page.find('div', id='cont1').findAll('th')
        for th in ths:
            a = th.find('a')
            if a and a['href']:
                return self.court.url + a['href'] + '&nc=1'
        return

    def get_result_text(self, url):
        # получаем текст решения
        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            print("GET error: ", status_code)
            return None
        page = BeautifulSoup(txt, 'html.parser')
        result_text_span = page.find('span')
        return strip_tags(result_text_span.text)

    def get_raw_case_information(self, url):
        # парсим карточку дела
        case_info = {}
        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            print("GET error: ", status_code)
            return
        page = BeautifulSoup(txt, 'html.parser')
        case_info['case_number'] = page.find('div', class_='casenumber').text.replace('ДЕЛО № ', '')
        case_info['url'] = url
        case_result_text_url = self.get_result_text_url(page)
        if case_result_text_url:
            result_text = self.get_result_text(case_result_text_url)
            case_info['result_text'] = result_text
        case_trs = page.find('div', id='cont1').find('tr').findAll('tr')
        for tr in case_trs:
            tds = tr.findAll('td')
            if len(tds) < 2:
                continue
            val = tds[1].text
            tr_text = tr.text
            if 'Уникальный идентификатор дела' in tr_text:
                case_info['case_uid'] = val
            if 'Дата поступления' in tr_text:
                case_info['entry_date'] = val
            if 'Номер протокола об АП' in tr_text:
                case_info['protocol_number'] = val
            if 'Судья' in tr_text or 'Передано в производство судье' in tr_text:
                case_info['judge'] = val
            if 'Дата рассмотрения' in tr_text or 'Дата вынесения постановления (определения) по делу' in tr_text:
                case_info['result_date'] = val
            if 'Результат рассмотрения' in tr_text:
                case_info['result_type'] = val
        if page.find('div', id='cont2'):
            events = []
            tr_head = [x.text for x in page.find('div', id='cont2').findAll('td')][1:]
            trs = page.find('div', id='cont2').findAll('tr')[2:-1]

            for tr in trs:
                event = {}
                tds = tr.findAll('td')
                event['type'] = tds[0].text.replace('\xa0', '')
                event['date'] = tds[1].text.replace('\xa0', '')
                if 'Время' in tr_head:
                    index = tr_head.index('Время')
                    event['time'] = tds[index].text.replace('\xa0', '')
                if 'Зал судебного заседания' in tr_head:
                    index = tr_head.index('Зал судебного заседания')
                    event['courtroom'] = tds[index].text.replace('\xa0', '')
                if 'Результат события' in tr_head:
                    index = tr_head.index('Результат события')
                    event['result'] = tds[index].text.replace('\xa0', '').strip()
                events.append(event)
            case_info['events'] = events
        if page.find('div', id='cont3'):
            defenses = []
            # trs = page.find('div', id='cont3').findAll('tr')
            case_info['defenses'] = self.parse_defenses(page.find('div', id='cont3'))
        if page.find('div', id='cont4'):
            trs = page.find('div', id='cont4').findAll('tr')
            for tr in trs:
                tr_text = tr.text
                if 'Дата направления дела в вышест. суд' in tr_text:
                    case_info['forwarding_to_higher_court_date'] = tr.findAll('td')[1].text.replace('\xa0', '').strip()
                if 'Дата рассмотрения жалобы' in tr_text:
                    case_info['appeal_date'] = tr.findAll('td')[1].text.replace('\xa0', '').strip()
                if 'Результат обжалования' in tr_text:
                    case_info['appeal_result'] = tr.findAll('td')[1].text.replace('\xa0', '').strip()
                if 'Дата возврата в нижестоящий суд' in tr_text:
                    case_info['forwarding_to_lower_court_date'] = tr.findAll('td')[1].text.replace('\xa0', '').strip()

        return case_info


class SecondParser(RFCourtSiteParser):

    # в системе судрф есть 2 типа сайтов судов, здесь мы обрабатываем первый (как https://bezhecky--twr.sudrf.ru)

    def get_pages_number(self, page):
        # получаем число страниц с делами
        pagination = page.find('ul', class_='pagination')
        if pagination:
            last_page_href = pagination.findAll('li')[-1].find('a')['href']
            pages_number = int(get_query_key(last_page_href, '_page'))
            return pages_number
        else:
            return 1

    def get_cases_urls_from_list(self, page):
        # получаем урлы карточек дел из страницы поиска
        urls = []

        a_cases = page.findAll('a', class_='open-lawcase')
        for a in a_cases:
            if Case.objects.filter(url=a['href']).exists():
                continue
            urls.append(a['href'] + '&nc=1')
        return urls

    def get_raw_case_information(self, url):

        #парсим карточку дела
        case_info = {}
        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            print("GET error: ", status_code)
            return None
        page = BeautifulSoup(txt, 'html.parser')
        case_info['case_number'] = page.find('div', class_='case-num').text.replace('дело № ', '')
        case_info['url'] = url
        case_result_text_div = page.find('div', id='tab_content_Document1')
        if case_result_text_div:
            case_result_text = strip_tags(case_result_text_div)
            case_info['result_text'] = case_result_text
        case_trs = page.find('div', id='tab_content_Case').findAll('tr')
        for tr in case_trs:
            tr_text = tr.text
            tds = tr.findAll('td')
            if len(tds) < 2:
                continue
            val = tds[1].text
            if 'Уникальный идентификатор дела' in tr_text:
                case_info['case_uid'] = val
            if 'Дата поступления' in tr_text:
                case_info['entry_date'] = val
            if 'Номер протокола об АП' in tr_text:
                case_info['protocol_number'] = val
            if 'Судья' in tr_text or 'Передано в производство судье' in tr_text:
                case_info['judge'] = val
            if 'Дата рассмотрения' in tr_text or 'Дата вынесения постановления (определения) по делу' in tr_text:
                case_info['result_date'] = val
            if 'Результат рассмотрения' in tr_text:
                case_info['result_type'] = val

        events_trs = page.find('div', id='tab_content_EventList').findAll('tr')[1:]
        tr_head = [x.text for x in page.find('div', id='tab_content_EventList').findAll('td')]
        events = []
        for tr in events_trs:
            event = {}
            tds = tr.findAll('td')
            event['type'] = tds[0].text.replace('\xa0', '')
            event['date'] = tds[1].text.replace('\xa0', '')
            if 'Время' in tr_head:
                index = tr_head.index('Время')
                event['time'] = tds[index].text.replace('\xa0', '')
            if 'Зал судебного заседания' in tr_head:
                index = tr_head.index('Зал судебного заседания')
                event['courtroom'] = tds[index].text.replace('\xa0', '')
            if 'Результат события' in tr_head:
                index = tr_head.index('Результат события')
                event['result'] = tds[index].text.replace('\xa0', '').strip()
            events.append(event)
        case_info['events'] = events

        # defendant_tds = page.find('div', id='tab_content_PersonList').findAll('tr')[1].findAll('td')
        defenses = []
        # trs = page.find('div', id='tab_content_PersonList').find('table', class_='none-mobile').findAll('tr')

        defense_table = page.find('div', id='tab_content_PersonList').find('table', class_='none-mobile')

        case_info['defenses'] = self.parse_defenses(defense_table)

        return case_info


class RFCasesGetter(CommonParser):

    def __init__(self, codex):
        self.codex = codex
        self.site_params = site_types_by_codex[self.codex]

    @staticmethod
    def generate_articles_string(articles):
        params_string = ''
        for article in articles:
            if article.part:
                params_string += f'&lawbookarticles[]={article.article_number}+ .{article.part}'
            else:
                params_string += f'&lawbookarticles[]={article.article_number}'

        return params_string.replace('[]', '%5B%5D').replace(' ', '%F7')

    @staticmethod
    def generate_params(string, params_dict, params):
        result_string = ''
        result_string += string
        for k, v in params.items():
            if k in params_dict:
                result_string += '&{0}={1}'.format(params_dict[k], v)
        return result_string

    def generate_url(self, court, params, instance):
        site_type = str(court.site_type)
        string = self.site_params[site_type]['string']
        delo_id, case_type, delo_table = instances_dict[self.codex][str(instance)]
        string = string.replace('DELOID', delo_id).replace('CASETYPE', case_type).replace('DELOTABLE', delo_table)
        params_dict = self.site_params[site_type]['params_dict']
        params_string = self.generate_params(string, params_dict, params)
        if instance == 2:
            params_string = params_string.replace('adm', 'adm1').replace('adm11', 'adm1')
        print(court.url + params_string)
        return court.url + params_string

    def get_cases(self, instance, courts_ids=None, courts_limit=None, entry_date_from=None):
        start_time = time.time()
        articles = CodexArticle.objects.filter(codex=self.codex)
        article_string = self.generate_articles_string(articles)
        if not courts_ids:
            courts = Court.objects.all()
        else:
            courts = Court.objects.filter(pk__in=courts_ids)
        if courts_limit:
            courts = courts[:courts_limit]

        for court in courts:
            params = {'articles': article_string}
            if entry_date_from:
                params['entry_date_from'] = entry_date_from  # DD.MM.YYYY
            url = self.generate_url(court, params, instance)
            if court.site_type == 2:
                url = url.replace('XXX', court.vn_kod)
                print(url, "WTF")
                SecondParser(court=court, stage=instance, codex=self.codex, url=url).save_cases()
            elif court.site_type == 1:
                FirstParser(court=court, stage=instance, codex=self.codex, url=url).save_cases()
        print("--- %s seconds ---" % (time.time() - start_time))

