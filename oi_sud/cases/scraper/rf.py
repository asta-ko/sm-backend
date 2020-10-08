import logging
from datetime import datetime
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from oi_sud.cases.consts import *
from oi_sud.cases.parsers.rf import FirstParser, SecondParser
from oi_sud.codex.models import CodexArticle
from oi_sud.courts.models import Court

from .main import Scraper

logger = logging.getLogger(__name__)


class RFScraper(Scraper):
    __slots__ = ()

    @staticmethod
    def generate_articles_string(codex, articles_string=None, active=True):

        # на входе список статей, на выходе get параметры для поиска

        if not articles_string:
            articles = CodexArticle.objects.filter(codex=codex, active=active)
        else:
            articles_list = articles_string.split(', ')
            articles = CodexArticle.objects.get_from_list(articles_list)
            if not len(articles):
                raise Exception('Could not get custom articles')

        params_string = ''
        for article in articles:
            if article.part:
                params_string += f'&lawbookarticles[]={article.article_number}+ .{article.part}'
            else:
                params_string += f'&lawbookarticles[]={article.article_number}'

        return params_string.replace('[]', '%5B%5D').replace(' ', '%F7')

    @staticmethod
    def generate_params(string, params_dict, params):
        formatted_params = {}
        for k, v in params.items():
            if k in params_dict and k != 'articles':
                formatted_params[params_dict[k]] = v
        params_string = urlencode(formatted_params, encoding='Windows-1251')
        result_string = f'{string}&{params_string}'
        if params.get("articles"):
            result_string += f'&{params_dict["articles"]}={params["articles"]}'
        return result_string

    def generate_url(self, court, params, instance, codex):
        site_type = str(court.site_type)
        site_params = site_types_by_codex[codex]
        string = site_params[site_type]['string']
        delo_id, case_type, delo_table = instances_dict[codex][str(instance)]
        string = string.replace('DELOID', delo_id).replace('CASETYPE', case_type).replace('DELOTABLE', delo_table)
        params_dict = site_params[site_type]['params_dict']
        params_string = self.generate_params(string, params_dict, params)
        if instance == 2:
            params_string = params_string.replace('adm', 'adm1').replace('adm11', 'adm1')
        return court.url + params_string

    def get_cases_urls_by_court(self, court, params, instance, codex):

        year = None

        if params.get('entry_date_from'):
            year = params['entry_date_from'].split('.')[-1]
        if params.get('entry_date_to') and params['entry_date_from'].split('.')[-1] != year:
            raise Exception('Invalid date params')

        url = self.generate_url(court, params, instance, codex)

        if court.site_type == 2:
            url = url.replace('XXX', court.vn_kod)
            cases_urls = SecondParser(court=court, stage=instance, codex=codex,
                                      url=url).get_all_cases_urls()
        elif court.site_type == 1:
            cases_urls = FirstParser(court=court, stage=instance, codex=codex,
                                     url=url).get_all_cases_urls()

        case_data = {'region': court.region, 'cases_urls': cases_urls, 'site_type': court.site_type, 'codex': codex,
                     'stage': instance, 'court_title': court.title, 'year': year}

        return case_data

    def get_rf_cases_urls(self, instance, codex, courts_ids=None, courts_limit=None, entry_date_from=None,
                          entry_date_to=None,
                          custom_articles=None, articles_active=True):

        result = []

        if isinstance(codex, int):
            codex = 'koap' if codex == 1 else 'uk'

        if not courts_ids:
            courts = Court.objects.exclude(type=9)
        else:
            courts = Court.objects.filter(pk__in=courts_ids)
        if courts_limit:
            courts = courts[:courts_limit]

        params = {
            'articles': self.generate_articles_string(codex, articles_string=custom_articles, active=articles_active)}
        if entry_date_from:
            params['entry_date_from'] = entry_date_from  # DD.MM.YYYY
        if entry_date_to:
            params['entry_date_to'] = entry_date_to  # DD.MM.YYYY

        for court in courts:
            data = self.get_new_rf_cases_for_court(court, params, instance, codex)
            result.append(data)

        return result

    def get_records_from_urls_data(self, urls_data):
        parser = None

        stage = urls_data['stage']
        codex = urls_data['codex']
        court = urls_data['court_title'].split(' (')[0]
        region = urls_data['region']
        year = urls_data['year']

        if urls_data['site_type'] == 1:
            parser = FirstParser()
        elif urls_data['site_type'] == 2:
            parser = SecondParser()

        records = []

        for url in urls_data['cases_urls']:
            case_html, status = parser.send_get_request(url)
            text_html = None

            case_html_lower = case_html.lower()

            if status != 200:
                logging.error('Failed to connect')
                continue
            if 'notice' in case_html_lower or \
                    'non-object' in case_html_lower or \
                    'pg_query' in case_html_lower or \
                    'pravosudie' in case_html_lower:
                logging.error("Bad page content")
                continue

            page = BeautifulSoup(case_html, 'html.parser')

            if urls_data['site_type'] == 1:
                case_result_text_url = parser.get_result_text_url(page)
                if case_result_text_url:
                    text_html, status = parser.send_get_request(case_result_text_url)

            records.append({'timestamp': datetime.now().timestamp(), 'case_url': url, 'text_url': case_result_text_url,
                            'case_html': case_html,
                            'text_html': text_html, 'stage': stage, 'codex': codex,
                            'court': court,
                            'year': year,
                            'region': region})
        return records

rf_sc = RFScraper()
