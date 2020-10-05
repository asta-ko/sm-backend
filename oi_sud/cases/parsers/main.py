import logging

import dateparser
import pytz
from dateparser.conf import settings as dateparse_settings
from django.utils.timezone import get_current_timezone
from oi_sud.cases.consts import APPEAL_RESULT_TYPES, EVENT_RESULT_TYPES, EVENT_TYPES, RESULT_TYPES
from oi_sud.cases.models import Case, Defendant, Advocate, Prosecutor
from oi_sud.cases.updater import merger_updater
from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.courts.models import Judge
from pytz import utc

logger = logging.getLogger(__name__)

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False

event_types_dict = {y: x for x, y in dict(EVENT_TYPES).items()}
event_result_types_dict = {y: x for x, y in dict(EVENT_RESULT_TYPES).items()}
result_types_dict = {y: x for x, y in dict(RESULT_TYPES).items()}
appeal_result_types_dict = {y: x for x, y in dict(APPEAL_RESULT_TYPES).items()}


class CourtSiteParser(CommonParser):
    __slots__ = ('court', 'url', 'codex', 'stage', 'article')

    def __init__(self, court=None, url=None, codex=None, stage=None, article=None):
        self.court = court
        self.url = url
        self.codex = codex
        self.stage = stage
        self.article = article

    def save_cases_from_df(self, records):

        for index, record in records.iterrows():

            raw_case_data = self.get_raw_case_information(record['case_url'], page_html=record['case_html'],
                                                          result_text_html=record['text_html'])

            serialized_case_data = self.serialize_data(raw_case_data)
            new_case = Case.objects.create_case_from_data(serialized_case_data)

            if new_case:
                merger_updater.process_duplicates(new_case)

    def check_url_actual(self, url):
        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            logging.error(f"GET error: unable to get rf cases - {status_code} {url}")
            raise Exception('Network error')
        txt = txt.lower()
        if 'notice' in txt or 'non-object' in txt or 'pg_query' in txt or 'pravosudie' in txt:
            return False
        return True

    def serialize_data(self, case_info):
        # сериализуем данные, полученные методом get_raw_case_information

        result = {'case': {}, 'defenses': [], 'events': [], 'codex_articles': []}

        for attribute in ['case_number', 'case_uid', 'protocol_number', 'result_text', 'linked_case_number',
                          'linked_case_url']:
            result['case'][attribute] = case_info.get(attribute)
        for attribute in ['case_number', 'case_uid', 'protocol_number']:
            if result['case'][attribute]:
                result['case'][attribute] = result['case'][attribute].replace(' ', '').replace('\n', '')

        for d in ['entry_date', 'result_date', 'result_published_date', 'result_valid_date',
                  'forwarding_to_higher_court_date', 'forwarding_to_lower_court_date', 'appeal_date']:
            if case_info.get(d):
                result['case'][d] = dateparser.parse(case_info[d], date_formats=['%d.%m.%Y'])

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
            if item.get('advocates'):
                item['advocates'] = [Advocate.objects.create_from_name(name=advocate_name, region=court.region) for
                                     advocate_name in item['advocates']]
            if item.get('prosecutors'):
                item['prosecutors'] = [Prosecutor.objects.create_from_name(name=prosecutor_name, region=court.region)
                                       for
                                       prosecutor_name in item['prosecutors']]

            item['defendant'] = defendant

        result['defenses'] = case_info['defenses']

        result['codex_articles'] = CodexArticle.objects.filter(pk__in=all_articles_ids)

        if case_info.get('judge'):
            try:
                result['case']['judge'] = Judge.objects.get_or_create(name=case_info['judge'], court=court)[0]
            except Judge.MultipleObjectsReturned:
                result['case']['judge'] = Judge.objects.filter(name=case_info['judge'], court=court).first()

        return result
