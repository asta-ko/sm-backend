import dateparser
import re
import time
import traceback
import pprint
from bs4 import BeautifulSoup
from dateparser.conf import settings as dateparse_settings
from django.utils.html import strip_tags
from django.utils.timezone import get_current_timezone, localtime

from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.core.utils import get_query_key
from oi_sud.courts.models import Court, Judge
from .consts import site_types_by_codex, EVENT_TYPES, EVENT_RESULT_TYPES, RESULT_TYPES
from .models import Case, CaseEvent, CaseDefense, Defendant

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False

event_types_dict = {y: x for x, y in dict(EVENT_TYPES).items()}
event_result_types_dict = {y: x for x, y in dict(EVENT_RESULT_TYPES).items()}
result_types_dict = {y: x for x, y in dict(RESULT_TYPES).items()}

from pytz import timezone, utc
# class OldCasesParser(CommonParser):
#     pass
#
# class MoscowNewCasesParser(CommonParser):
#     pass
#
# class MJudgesCasesParser(CommonParser):
#     pass


class CourtSiteParser(CommonParser):

    def __init__(self, court=None, url=None, type=None, stage=None):
        self.court = court
        self.url = url
        self.type = type
        self.stage = stage

    def save_cases(self, urls=None):

        print(self.court)

        if not urls:
            urls = self.get_all_cases_urls()#[:5]  # [:50]

        if not urls:
            return

        for case_url in urls:
            try:
                raw_case_data = self.get_raw_case_information(case_url)
                if not raw_case_data:
                    continue
                serialized_case_data = self.serialize_data(raw_case_data)
                Case.objects.create_case_from_data(serialized_case_data)
            except:
                print('error: ', case_url)
                print(traceback.format_exc())

    def get_all_cases_urls(self):
        txt, status_code = self.send_get_request(self.url)
        if status_code != 200:
            print("GET error: ", status_code)
            print('Unable to save cases')
            return None
        first_page = BeautifulSoup(txt, 'html.parser')
        pages_number = self.get_pages_number(first_page)  # TODO CHANGE
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
                urls = [self.url.replace('/modules.php', '').split('?')[0] + u for u in urls]
                all_cases_urls += urls
            except AttributeError:
                pass

        if all_cases_urls == []:
            print(self.court, '...Got no cases urls')
        else:
            print(self.court, '...Got all cases urls')

        return all_cases_urls

    def get_koap_article(self, raw_string):

        m = re.search(r'КоАП:\sст\.\s([0-9\.]+)\s?ч?\.?([0-9\.]*)', raw_string)

        if m:
            article = m.group(1)
            part = m.group(2)
            codex_article = CodexArticle.objects.filter(codex='koap', article_number=article, part=part).first()
            if codex_article:
                return [codex_article]
        return []

    def get_uk_articles(self, raw_string):
        raw_list = list(set(raw_string.replace('УК РФ', '').split(';')))
        codex_articles = []
        for item in raw_list:
            codex_article = None
            item = item.strip()
            m = re.search(r'ст\.([0-9\.]+)\s?ч?\.?([0-9\.]*)', item)
            if m:
                article = m.group(1)
                part = m.group(2)
                codex_article = CodexArticle.objects.filter(codex='uk', article_number=article, part=part).first()
            if codex_article:
                codex_articles.append(codex_article)
        return codex_articles

    def normalize_date(self, datetime):


        local_dt = self.court.get_timezone().localize(dateparser.parse(datetime, date_formats=['%d.%m.%Y']))
        return utc.normalize(local_dt.astimezone(utc))

    def serialize_data(self, case_info):

        result = {'case': {}, 'defenses': [], 'events': [],  'codex_articles': []}

        for attribute in ['case_number', 'case_uid', 'protocol_number', 'result_text']:
            result['case'][attribute] = case_info.get(attribute)

        result['case']['entry_date'] = self.normalize_date(case_info['entry_date']).date()
        if case_info.get('result_date'):
            result['case']['result_date'] = self.normalize_date(case_info['result_date']).date()
        if case_info.get('result_published'):
            result['case']['result_published'] = self.normalize_date(case_info['result_published']).date()
        if case_info.get('result_valid'):
            result['case']['result_valid'] = self.normalize_date(case_info['result_valid']).date()
        if case_info.get('result_type'):
            result['case']['result_type'] = result_types_dict[case_info['result_type'].strip()]
        result['case']['url'] = case_info['url'].replace('&nc=1', '')
        result['case']['court'] = self.court
        result['case']['type'] = self.type
        result['case']['stage'] = self.stage

        all_articles_ids = []

        for item in case_info['events']:
            result_item = {}
            if item.get('courtroom'):
                result_item['courtroom'] = int(''.join(filter(str.isdigit, item['courtroom'])))
            result_item['type'] = event_types_dict[item['type'].strip()]
            if item.get('date'):
                d = dateparser.parse(f'{item.get("date")} {item.get("time")}')
                if d:
                    local_dt = self.court.get_timezone().localize(d)
                    result_item['date'] = utc.normalize(local_dt.astimezone(utc))
            if item.get('result'):
                result_item['result'] = event_result_types_dict[item['result'].strip()]
            result['events'].append(result_item)

        for item in case_info['defenses']:
            if self.type == 1:
                article = item['codex_articles'] = self.get_koap_article(item['codex_articles'])  # TODO: КАС и ГПК
                if len(article) and article[0] not in all_articles_ids:  # TODO: NON POLITICAL ARTICLES
                    all_articles_ids.append(article[0].id)
            elif self.type == 2:
                articles = item['codex_articles'] = self.get_uk_articles(item['codex_articles'])
                for article in articles:
                    if article.id not in all_articles_ids:
                        all_articles_ids.append(article.id)
            defendant_name = item['defendant']
            defendant, created = Defendant.objects.get_or_create(name=defendant_name, region=self.court.region)
            item['defendant'] = defendant

        result['defenses'] = case_info['defenses']
        result['codex_articles'] = CodexArticle.objects.filter(pk__in=all_articles_ids)

        if case_info.get('judge'):
            judge, created = Judge.objects.get_or_create(name=case_info['judge'], court=self.court)
            result['case']['judge'] = judge

        return result

class FirstParser(CourtSiteParser):

    def get_pages_number(self, page):

        pagination_a = page.find('a', attrs={'title': 'На последнюю страницу списка'})
        if not pagination_a:
            return 1
        else:
            last_page_href = pagination_a['href']
            pages_number = int(get_query_key(last_page_href, 'page'))
            return pages_number

    def get_cases_urls_from_list(self, page):
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
        ths = page.find('div', id='cont1').findAll('th')
        for th in ths:
            a = th.find('a')
            if a and a['href']:
                return self.court.url + a['href'] + '&nc=1'
        return

    def get_result_text(self, url):
        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            print("GET error: ", status_code)
            return None
        page = BeautifulSoup(txt, 'html.parser')
        result_text_span = page.find('span')
        return strip_tags(result_text_span.text)

    def get_raw_case_information(self, url):
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
            if 'Судья' in tr_text:
                case_info['judge'] = val
            if 'Дата рассмотрения' in tr_text:
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
            trs = page.find('div', id='cont3').findAll('tr')[2:]

            for tr in trs:
                tds = tr.findAll('td')
                if len(tds) > 2:
                    codex_articles, defendant = None, None
                    if self.type == 1:
                        codex_articles = tds[2].text.strip()
                        defendant = tds[1].text.strip()
                    elif self.type == 2:
                        codex_articles = tds[1].text.strip()
                        defendant = tds[0].text.strip()
                    defenses.append({'defendant': defendant, 'codex_articles': codex_articles})
            case_info['defenses'] = defenses

        return case_info


class SecondParser(CourtSiteParser):

    def get_pages_number(self, page):
        pagination = page.find('ul', class_='pagination')
        if pagination:
            last_page_href = pagination.findAll('li')[-1].find('a')['href']
            pages_number = int(get_query_key(last_page_href, '_page'))
            return pages_number
        else:
            return 1

    def get_cases_urls_from_list(self, page):
        urls = []

        a_cases = page.findAll('a', class_='open-lawcase')
        for a in a_cases:
            if Case.objects.filter(url=a['href']).exists():
                continue
            urls.append(a['href'] + '&nc=1')
        return urls

    def get_raw_case_information(self, url):

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
            if 'Судья' in tr_text:
                case_info['judge'] = val
            if 'Дата рассмотрения' in tr_text:
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
        trs = page.find('div', id='tab_content_PersonList').find('table', class_='none-mobile').findAll('tr')[1:]
        for tr in trs:
            codex_articles = tr.findAll('td')[2].text.strip()
            defendant = tr.findAll('td')[1].text.strip()
            defenses.append({'defendant': defendant, 'codex_articles': codex_articles})
        case_info['defenses'] = defenses

        return case_info


class RFCasesParser(CommonParser):

    def __init__(self, codex):
        self.codex = codex
        if self.codex == 'koap':
            self.type = 1
        elif self.codex == 'uk':
            self.type = 2
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

    def generate_url(self, court, params):
        site_type = str(court.site_type)
        string = self.site_params[site_type]['string']
        params_dict = self.site_params[site_type]['params_dict']
        return court.url + self.generate_params(string, params_dict, params)

    def get_cases_first_instance(self, courts=None, courts_limit=None, entry_date_from=None):
        start_time = time.time()
        articles = CodexArticle.objects.filter(codex=self.codex)
        article_string = self.generate_articles_string(articles)
        if not courts:
            courts = Court.objects.all()
        if courts_limit:
            courts = courts[:courts_limit]

        for court in courts:
            params = {'articles': article_string}
            if entry_date_from:
                params['entry_date_from'] = entry_date_from  # DD.MM.YYYY
            url = self.generate_url(court, params)
            if court.site_type == 2:
                url = url.replace('XXX', court.vn_kod)
                SecondParser(court=court, stage=1, type=self.type, url=url).save_cases()
            elif court.site_type == 1:
                FirstParser(court=court, stage=1, type=self.type, url=url).save_cases()
        print("--- %s seconds ---" % (time.time() - start_time))

    def update_cases(self):

        for case in Case.objects.filter(type=self.type):

            if case.court.site_type == 1:
                p = FirstParser(court=case.court, stage=1, type=self.type)
            elif case.court.site_type == 2:
                p = SecondParser(court=case.court, stage=1, type=self.type)

            raw_data = p.get_raw_case_information(case.url)
            fresh_data =  {i:j for i,j in p.serialize_data(raw_data).items() if j != None}
            case.update_if_needed(fresh_data)

