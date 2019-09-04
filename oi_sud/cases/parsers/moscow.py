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
            href = 'https://www.mos-gorsud.ru'+ev_cols[0]('a')[0]['href']
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
                print(urls, 'urls0')
                #urls = [self.url.replace('/modules.php', '').split('?')[0] + u for u in urls]
                all_cases_urls += urls
            except AttributeError:
                pass

        if all_cases_urls == []:
            print('...Got no cases urls')
        else:
            print('...Got all cases urls')

        return all_cases_urls

    def get_raw_case_information(self, url):

        court = self.get_court_from_url(url)

        # парсим карточку дела

        # return case_info = {'case_number':'',
        #      'url':'',
        #      'result_text':'',
        #      'case_uid':'',
        #      'entry_date':'',
        #      'protocol_number':'',
        #      'judge':'',
        #      'result_date':'',
        #      'result_type':'',
        #      'events':[{'type':'','date':'', 'time':'','courtroom':'','result':''}, {...}, {...}],
        #      'defenses':[{'defendant': defendant, 'codex_articles': codex_articles'}, {...}, {...}],
        #      'forwarding_to_higher_court_date':'',
        #      'appeal_date':'',
        #      'appeal_result':'',
        #      'forwarding_to_lower_court_date':''}
        raise NotImplementedError

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
            articles = CodexArticle.objects.get_from_list(articles_list).filter(codex=codex)
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

            MoscowParser(url=url, stage=instance).save_cases()