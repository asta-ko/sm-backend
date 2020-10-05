# coding=utf-8
import logging
from datetime import datetime

from bs4 import BeautifulSoup
from oi_sud.cases.consts import moscow_params_dict
from oi_sud.cases.parsers.moscow import MoscowParser
from oi_sud.codex.models import CodexArticle
from oi_sud.core.textract import DocParser, DocXParser, RTFParser

from .main import Scraper

logger = logging.getLogger(__name__)


class MoscowScraper(Scraper):

    def try_to_parse_result_text(self, parser, filename):
        try:
            text = parser.process(filename, 'utf-8')
            return text
        except Exception as e:
            return ''

    def url_to_str(self, url):
        """ выгружает текст из файла doc / docx, загружаемого по ссылке """
        file_res, status, content, extension = self.send_get_request(url, extended=True)

        bytes0 = content  # file_res#[2]
        filename = "txt"
        if extension:
            filename += f'.{extension}'
        f = open(filename, 'wb')
        f.write(bytes0)
        f.close()
        if extension == 'rtf':
            return self.try_to_parse_result_text(RTFParser(), filename)
        if extension == 'docx':
            return self.try_to_parse_result_text(DocXParser(), filename)
        elif extension == 'doc':
            return self.try_to_parse_result_text(DocParser(), filename)
        elif not extension:
            docx = self.try_to_parse_result_text(DocXParser(), filename)
            rtf = self.try_to_parse_result_text(RTFParser(), filename)
            doc = self.try_to_parse_result_text(DocParser(), filename)

            if not (docx or rtf or doc):
                logger.critical(f'{url}: Could not process moscow result text file')

            return docx or rtf or doc

        else:
            logger.critical(f'{url}: Could not process moscow result text file')

    @staticmethod
    def generate_params(url_string, params):
        params_string = ''
        # result_string += string
        for k, v in params.items():
            if k in moscow_params_dict:
                params_string += '&{0}={1}'.format(moscow_params_dict[k], v)
        params_string = '?' + params_string[1:]

        return url_string + params_string

    def get_cases_urls_by_court(self, court, params, instance, codex, articles_list=None):

        year = None

        if params.get('entry_date_from'):
            year = params['entry_date_from'].split('.')[-1]
        if params.get('entry_date_to') and params['entry_date_from'].split('.')[-1] != year:
            raise Exception('Invalid date params')

        court_alias = court.url.split('/')[-1]

        process_type = '3' if codex == 'koap' else '6'  # 3 for koap, 6 for uk

        if articles_list:
            articles = CodexArticle.objects.get_from_list(articles_list, codex=codex)
        else:
            articles = CodexArticle.objects.filter(codex=codex, active=True)

        koap_uk_space = ''
        if codex == 'uk':
            koap_uk_space = '%20'

        case_data = {'region': court.region, 'cases_urls': [], 'site_type': court.site_type, 'codex': codex,
                     'stage': instance, 'court_title': court.title, 'year': year}

        for article in articles:
            article_string = f'Ст.%20{article.article_number},%20Ч.{koap_uk_space}{article.part}' if article.part else f'Ст.%20{article.article_number}'
            params = {'articles': article_string, 'instance': instance, 'courtAlias': court_alias,
                      'processType': process_type}
            url = self.generate_params('https://mos-gorsud.ru/mgs/search', params)
            article_urls = MoscowParser(url=url, article=article).get_all_cases_urls()
            case_data['cases_urls'] += article_urls

        return case_data

    def get_records_from_urls_data(self, urls_data):

        # получаем html для последующего сохранения

        stage = urls_data['stage']
        codex = urls_data['codex']
        court = urls_data['court_title'].split(' (')[0]
        region = urls_data['region']
        year = urls_data['year']

        records = []

        parser = MoscowParser()

        for url in urls_data['cases_urls']:
            case_html, status = parser.send_get_request(url)

            if status == 200:
                page = BeautifulSoup(case_html, 'html.parser')

                case_result_text_url = parser.get_result_text_url(page)

                text_html = self.url_to_str(case_result_text_url) if case_result_text_url else None

                records.append(
                    {'timestamp': datetime.now().timestamp(), 'case_url': url, 'text_url': case_result_text_url,
                     'case_html': case_html,
                     'text_html': text_html, 'stage': stage, 'codex': codex,
                     'court': court,
                     'year': year,
                     'region': region})
        return records


moscow_sc = MoscowScraper()
