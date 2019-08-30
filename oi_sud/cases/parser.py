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
from oi_sud.cases.utils import normalize_name
from oi_sud.courts.models import Court, Judge
from .consts import site_types_by_codex, EVENT_TYPES, EVENT_RESULT_TYPES, RESULT_TYPES, APPEAL_RESULT_TYPES, instances_dict
from .models import Case, Defendant
from dateutil.relativedelta import relativedelta

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False

event_types_dict = {y: x for x, y in dict(EVENT_TYPES).items()}
event_result_types_dict = {y: x for x, y in dict(EVENT_RESULT_TYPES).items()}
result_types_dict = {y: x for x, y in dict(RESULT_TYPES).items()}
appeal_result_types_dict = {y: x for x, y in dict(APPEAL_RESULT_TYPES).items()}

from pytz import timezone, utc


class CourtSiteParser(CommonParser):

    def __init__(self, court=None, url=None, type=None, stage=None):
        self.court = court
        self.url = url
        self.type = type
        self.stage = stage

    def parse_defenses(self, el):
        defenses = []
        title_tr = None
        title_tr_index = None
        title_tds = []
        defendant_index = None
        codex_articles_index = None
        trs = el.findAll('tr')
        for index, tr in enumerate(trs):

            tr_text = tr.text
            #print(tr_text, 'tr_text')
            if 'ФИО' in tr_text or 'Фамилия' in tr_text or 'статей' in tr_text:
                title_tr = tr
                title_tr_index = index

        if not title_tr:
            title_tds = el.findAll('td', attrs={'align':'center'})
            title_tr_index = 2
        else:
            title_tds = title_tr.findAll('td')

        for index, td in enumerate(title_tds):
            td_text = td.text
            if 'ФИО' in td_text or 'Фамилия' in td_text:
                defendant_index = index
                #print(defendant_index, 'defeant_index')
            if 'статей' in td_text:
                codex_articles_index = index

        for tr in trs[title_tr_index:]:
            if 'ФИО' in tr.text or 'статей' in tr.text or 'Фамилия' in tr.text or 'Информация скрыта' in tr.text:
                continue
            tds = tr.findAll('td')
            if len(tds)>=defendant_index and len(tds) >= codex_articles_index:
                defendant = tds[defendant_index].text.strip()
                codex_articles = tds[codex_articles_index].text.strip()
                print(defendant, codex_articles)
                defenses.append({'defendant': defendant, 'codex_articles': codex_articles})

        return defenses

    def save_cases(self, urls=None):

        print(self.court)

        if not urls:
            urls = self.get_all_cases_urls()#[:5]  # [:50]

        if not urls:
            return

        for case_url in urls:
            try:
                u = case_url.replace('&nc=1','')
                if Case.objects.filter(url=u).exists():
                    continue
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
        if case_info.get('forwarding_to_higher_court_date'):
            result['case']['forwarding_to_higher_court_date'] = self.normalize_date(case_info['forwarding_to_higher_court_date']).date()
        if case_info.get('forwarding_to_lower_court_date'):
            result['case']['forwarding_to_lower_court_date'] = self.normalize_date(case_info['forwarding_to_lower_court_date']).date()
        if case_info.get('appeal_date'):
            result['case']['appeal_date'] = self.normalize_date(case_info['appeal_date']).date()
        if case_info.get('appeal_result'):
            result['case']['appeal_result'] = appeal_result_types_dict[case_info['appeal_result']]
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
            defendant = Defendant.objects.create_from_name(name=defendant_name, region=self.court.region)
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
            #trs = page.find('div', id='cont3').findAll('tr')
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
        #trs = page.find('div', id='tab_content_PersonList').find('table', class_='none-mobile').findAll('tr')

        defense_table =  page.find('div', id='tab_content_PersonList').find('table', class_='none-mobile')

        case_info['defenses'] = self.parse_defenses(defense_table)

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
                SecondParser(court=court, stage=instance, type=self.type, url=url).save_cases()
            elif court.site_type == 1:
                FirstParser(court=court, stage=instance, type=self.type, url=url).save_cases()
        print("--- %s seconds ---" % (time.time() - start_time))

    def update_cases(self):

        for case in Case.objects.filter(type=self.type):
            try:
                if case.court.site_type == 1:
                    p = FirstParser(court=case.court, stage=1, type=self.type)
                elif case.court.site_type == 2:
                    p = SecondParser(court=case.court, stage=1, type=self.type)
                url = case.url + '&nc=1'
                # print(url)
                raw_data = p.get_raw_case_information(url)
                fresh_data =  {i:j for i,j in p.serialize_data(raw_data).items() if j != None}
                case.update_if_needed(fresh_data)
            except:
                print('error: ', case.url)
                print(traceback.format_exc())

    def get_first_cases(self, case):

        params = {'stage':1, 'defendants__in':case.defendants.all()}
        other_params_list = []

        if case.result_date:
            other_params_list.append({'appeal_date': case.result_date})
        if case.case_uid:
            other_params_list.append({'case_uid': case.case_uid})
        if case.protocol_number:
            other_params_list.append({'protocol_number': case.protocol_number})
            other_params_list.append({'result_text__contains': case.protocol_number})

        for item in other_params_list:
            merged_params = {**params, **item}
            # print(merged_params)
            if Case.objects.filter(**merged_params).exists():
                # print(item)
                return Case.objects.filter(**merged_params)

    def get_second_case(self, case):
        params = {'stage':2, 'defendants__in':case.defendants.all()}
        other_params_list = []

        if case.appeal_date:
            other_params_list.append({'result_date':case.appeal_date})
        if case.case_uid:
            other_params_list.append({'case_uid':case.case_uid})
        if case.protocol_number:
            other_params_list.append({'protocol_number':case.protocol_number})
            other_params_list.append({'result_text__contains':case.protocol_number})

        other_params_list.append({'result_text__contains':case.case_number})

        for item in other_params_list:
            merged_params = {**params, **item}
            #print(merged_params)
            if Case.objects.filter(**merged_params).exists():
                #print(item)
                return Case.objects.filter(**merged_params)

    def group_cases(self, region):

        first_cases_appealed = Case.objects.filter(court__region=region, appeal_result__isnull=False, linked_cases=None)
        second_cases = Case.objects.filter(stage=2, court__region=region)
        for case in first_cases_appealed:
            second_cases = self.get_second_case(case)
            if second_cases:
                case.linked_cases.add(*second_cases)

        first_cases_not_found = Case.objects.filter(stage=1, court__region=region, appeal_result__isnull=False, linked_cases=None)
        second_instance_cases_not_found = Case.objects.filter(stage=2, court__region=region, linked_cases=None)

        #print(len(first_cases_appealed), 'first_cases_appealed')
        print(len(first_cases_not_found), 'first_cases_not_found')
        #print(len(second_cases), 'second_cases_all')
        print(len(second_instance_cases_not_found), 'second_cases_not_found')

        for case in second_instance_cases_not_found:
            first_cases = self.get_first_cases(case)
            if first_cases:
                case.linked_cases.add(*first_cases)
                print('Yikes!')

        first_cases_not_found = Case.objects.filter(stage=1, court__region=region, appeal_result__isnull=False, linked_cases=None)
        second_instance_cases_not_found = Case.objects.filter(stage=2, court__region=region, linked_cases=None)
        #print(len(first_cases_appealed), 'first_cases_appealed')
        print(len(first_cases_not_found), 'first_cases_not_found')
        #print(len(second_cases), 'second_cases_all')
        print(len(second_instance_cases_not_found), 'second_cases_not_found')

        for case in first_cases_not_found:
            c = second_instance_cases_not_found.filter(defendants__in=case.defendants.all(), entry_date__gte=case.result_date, entry_date__lte=case.result_date+relativedelta(months=3))
            if len(c):
                case.linked_cases.add(*c)

        for case in second_instance_cases_not_found:
            c = first_cases_not_found.filter(defendants__in=case.defendants.all(), result_date__lt=case.entry_date, result_date__year=case.entry_date.year)
            if len(c):
                print([x.case_number for x in c])
                case.linked_cases.add(*c)

        # first_cases_not_found = Case.objects.filter(stage=1, court__region=region, appeal_result__isnull=False,
        #                                             linked_cases=None)
        # second_instance_cases_not_found = Case.objects.filter(stage=2, court__region=region, linked_cases=None)
        #
        # for case in first_cases_not_found:
        #     print(case.defendants.all())
        #
        # for case in second_instance_cases_not_found:
        #     print(case.defendants.all())