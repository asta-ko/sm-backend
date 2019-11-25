# coding=utf-8
import re
from bs4 import BeautifulSoup

from dateparser.conf import settings as dateparse_settings
from django.utils.timezone import get_current_timezone

from oi_sud.cases.consts import msudrf_params_dict
from oi_sud.cases.models import Case
from oi_sud.cases.parsers.main import CourtSiteParser
from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.core.utils import get_query_key
from oi_sud.courts.models import Court

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False



class MsudrfParser(CourtSiteParser):


    def get_pages_number(self, page):
        # получаем число страниц с делами (скорее всего больше одной будет редко, но делать нужно)

        raise NotImplementedError

    def get_cases_urls_from_list(self, page):
        # получаем урлы карточек дел из страницы поиска
        raise NotImplementedError

    def get_all_cases_urls(self, limit_pages=False):
        # Получаем все урлы дел по данной статье
        raise NotImplementedError



    def get_raw_case_information(self, url):


        #  case_info = {'case_number':'', # номер - обязательно
        #      'url':'', # урл - обязательно
        #      'result_text':'', # текст судебного решения
        #      'case_uid':'', # uid
        #      'entry_date':'', # дата поступления
        #      'protocol_number':'', # номер протокола (для административок)
        #      'judge':'', # судья
        #      'result_date':'', # дата конечного состояния
        #      'result_type':'', # тип конечного состояния
        #      'events':[{'type':'','date':'', 'time':'','courtroom':'','result':''}, {...}, {...}],
        #      'defenses':[{'defendant': defendant, #ответчик - обязательно
        #                    'codex_articles': codex_articles' #статья/и - обязательно
        #                    }, {...}, {...}],
        #return case_info

        raise NotImplementedError


    def get_result_text(self, url):
        # получаем текст решения
        txt, status_code = self.send_get_request(url)
        return NotImplementedError


    def get_koap_article(self, raw_string):
        # получаем объекты статей КОАП из строки, полученной из карточки дела
        raise NotImplementedError

    def get_uk_articles(self, raw_string):
        # получаем объекты статей УК из строки, полученной из карточки дела
        raise NotImplementedError

class MsudrfCasesGetter(CommonParser):

    @staticmethod
    def generate_params(string, params):

        result_string = ''
        result_string += string
        for k, v in params.items():
            if k in msudrf_params_dict:
                result_string += '&{0}={1}'.format(msudrf_params_dict[k], v)
        return result_string

    def get_cases(self, codex, entry_date_from=None, articles_list=None):
        # получаем дела по инстанции, типу производства

        courts = Court.objects.filter(site_type=4)

        if articles_list:
            articles = CodexArticle.objects.get_from_list(articles_list, codex=codex)
        else:
            articles = CodexArticle.objects.filter(codex=codex, active=True)

        for court in courts:
            for article in articles: #похоже, мы не можем искать сразу по списку статей

                url = self.generate_params()
                MsudrfParser(url=url, codex=codex).save_cases()
