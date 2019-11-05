import re
import pytz
import requests
import traceback
from bs4 import BeautifulSoup

import dateparser
from dateparser.conf import settings as dateparse_settings
from django.utils.timezone import get_current_timezone
from django.conf import settings

from oi_sud.cases.consts import EVENT_TYPES, EVENT_RESULT_TYPES, RESULT_TYPES, APPEAL_RESULT_TYPES
from oi_sud.cases.models import Case, Defendant
from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.courts.models import Judge

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False

event_types_dict = {y: x for x, y in dict(EVENT_TYPES).items()}
event_result_types_dict = {y: x for x, y in dict(EVENT_RESULT_TYPES).items()}
result_types_dict = {y: x for x, y in dict(RESULT_TYPES).items()}
appeal_result_types_dict = {y: x for x, y in dict(APPEAL_RESULT_TYPES).items()}

from pytz import utc


class CourtSiteParser(CommonParser):

    def __init__(self, court=None, url=None, codex=None, stage=None):
        self.court = court
        self.url = url
        self.codex = codex
        self.stage = stage

    def save_cases(self, urls=None, retrying=False):
        # Берем список урлов дел данного суда данной инстанции и сохраняем дела в базу. Это самый главный метод

        if not urls:
            urls = self.get_all_cases_urls()

        if not urls:
            return {'found':0}

        if settings.TEST_MODE:
            urls = urls[:2]

        result = {}
        result['found'] = len(urls)
        result['errors'] = 0
        result['proccessed'] = 0
        result['error_urls'] = []
        result['exist'] = 0
        result['new'] = 0

        for case_url in urls:
            try:
                u = case_url.replace('&nc=1', '')
                if Case.objects.filter(url=u).exists():
                    result['exist'] += 1
                    continue
                raw_case_data = self.get_raw_case_information(case_url)
                if not raw_case_data:
                    result['errors'] += 1
                    result['error_urls'].append(case_url)
                    continue
                serialized_case_data = self.serialize_data(raw_case_data)
                Case.objects.create_case_from_data(serialized_case_data)
                if self.court and case_url in self.court.unprocessed_cases_urls:
                    self.court.unprocessed_cases_urls.remove(case_url)
                    self.court.save()
                result['proccessed'] +=1
                result['new'] +=1
            except:
                print('error: ', case_url)
                print(traceback.format_exc())
                result['errors'] +=1
                result['error_urls'].append(case_url)

        if self.court:
            for error_url in result['error_urls']:
                if error_url not in self.court.unprocessed_cases_urls:
                    self.court.unprocessed_cases_urls.append(error_url)
            self.court.save()

        return result



    def normalize_date(self, datetime):
        if not self.court:
            timezone = pytz.timezone('Europe/Moscow')
        else:
            timezone = self.court.get_timezone()

        local_dt = timezone.localize(dateparser.parse(datetime, date_formats=['%d.%m.%Y']))
        return utc.normalize(local_dt.astimezone(utc))

    def serialize_data(self, case_info):
        # сериализуем данные, полученные методом get_raw_case_information

        result = {'case': {}, 'defenses': [], 'events': [], 'codex_articles': []}

        for attribute in ['case_number', 'case_uid', 'protocol_number', 'result_text', 'linked_case_number', 'linked_case_url']:
            result['case'][attribute] = case_info.get(attribute)
        for attribute in  ['case_number', 'case_uid', 'protocol_number']:
            if result['case'][attribute]:
                result['case'][attribute] = result['case'][attribute].replace(' ','').replace('\n','')
        if case_info.get('entry_date'):
            result['case']['entry_date'] = self.normalize_date(case_info['entry_date']).date()
        if case_info.get('result_date'):
            result['case']['result_date'] = self.normalize_date(case_info['result_date']).date()
        if case_info.get('result_published_date'):
            result['case']['result_published_date'] = self.normalize_date(case_info['result_published_date']).date()
        if case_info.get('result_valid_date'):
            result['case']['result_valid_date'] = self.normalize_date(case_info['result_valid_date']).date()
        if case_info.get('forwarding_to_higher_court_date'):
            result['case']['forwarding_to_higher_court_date'] = self.normalize_date(
                case_info['forwarding_to_higher_court_date']).date()
        if case_info.get('forwarding_to_lower_court_date'):
            result['case']['forwarding_to_lower_court_date'] = self.normalize_date(
                case_info['forwarding_to_lower_court_date']).date()
        if case_info.get('appeal_date'):
            result['case']['appeal_date'] = self.normalize_date(case_info['appeal_date']).date()
        if case_info.get('appeal_result'):
            result['case']['appeal_result'] = case_info['appeal_result'].strip()
        if case_info.get('result_type'):
            result['case']['result_type'] = case_info['result_type'].strip()
        result['case']['url'] = case_info['url'].replace('&nc=1', '')
        if case_info.get('defendants_hidden'):
            result['case']['defendants_hidden'] = True
        if self.court:
            result['case']['court'] = self.court
        elif case_info.get('court'):
            result['case']['court'] = case_info.get('court')

        if self.codex == 'koap':
            result['case']['type'] = 1
        elif self.codex == 'uk':
            result['case']['type'] = 2



        result['case']['stage'] = self.stage

        all_articles_ids = []

        court = self.court or case_info.get('court')

        for item in case_info['events']:
            result_item = {}
            if item.get('courtroom'):
                courtroom_string = ''.join(filter(str.isdigit, item['courtroom']))
                if courtroom_string:
                    result_item['courtroom'] = int(courtroom_string)
            result_item['type'] = item['type'].strip()
            if item.get('date'):
                if item.get('time'):
                    d = dateparser.parse(f'{item.get("date")} {item.get("time")}')
                else:
                    d = dateparser.parse(f'{item.get("date")}')
                if d:
                    if court:
                        timezone = court.get_timezone()
                    else:
                        timezone = pytz.timezone('Europe/Moscow')
                    local_dt = timezone.localize(d)
                    result_item['date'] = utc.normalize(local_dt.astimezone(utc))
            if item.get('result'):
                result_item['result'] = item['result'].strip()
            result['events'].append(result_item)

        for item in case_info['defenses']:
            if self.codex == 'koap':
                article = item['codex_articles'] = self.get_koap_article(item['codex_articles'])  # TODO: КАС и ГПК
                if len(article) and article[0] not in all_articles_ids:  # TODO: NON POLITICAL ARTICLES
                    all_articles_ids.append(article[0].id)
            elif self.codex == 'uk':
                articles = item['codex_articles'] = self.get_uk_articles(item['codex_articles'])
                for article in articles:
                    if article.id not in all_articles_ids:
                        all_articles_ids.append(article.id)
            defendant_name = item['defendant']
            defendant = Defendant.objects.create_from_name(name=defendant_name, region=court.region)
            item['defendant'] = defendant

        result['defenses'] = case_info['defenses']

        result['codex_articles'] = CodexArticle.objects.filter(pk__in=all_articles_ids)

        if case_info.get('judge'):
            judge, created = Judge.objects.get_or_create(name=case_info['judge'], court=court)
            result['case']['judge'] = judge

        return result
