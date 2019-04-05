from bs4 import BeautifulSoup

from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.core.utils import get_query_key
from oi_sud.courts.models import Court
from .consts import site_types_by_codex


# class OldCasesParser(CommonParser):
#     pass
#
# class MoscowNewCasesParser(CommonParser):
#     pass
#
# class MJudgesCasesParser(CommonParser):
#     pass


class CourtSiteParser(CommonParser):

    def get_cases(self, url):
        print(url)
        txt = self.send_get_request(url)
        page = BeautifulSoup(txt, 'html.parser')
        pages_number = self.get_pages_number(page)
        cases_urls = [url.replace('modules.php', '').split('?')[0] + u for u in self.get_cases_urls(page)]

        for case_url in cases_urls:
            self.get_case_information(case_url)


class FirstParser(CourtSiteParser):

    def get_pages_number(self, page):
        print('yay')

        pagination_a = page.find('a', attrs={'title': 'На последнюю страницу списка'})
        if not pagination_a:
            return 1
        else:
            last_page_href = pagination_a['href']
            pages_number = int(get_query_key(last_page_href, 'page'))
            return pages_number

    def get_cases_urls(self, page):
        urls = []
        tds = page.find('table', id='tablcont').findAll('td', attrs={
            'title': 'Для получения справки по делу, нажмите на номер дела'})
        for td in tds:
            href = td.find('a')['href']
            urls.append(href + '&nc=1')
        return urls

    def get_case_information(self, url):

        case_info = {}
        txt = self.send_get_request(url)
        page = BeautifulSoup(txt, 'html.parser')
        case_trs = page.find('div', id='cont1').find('tr').findAll('tr')
        for tr in case_trs[4:]:
            val = tr.findAll('td')[1].text
            tr_text = tr.text
            if 'Уникальный идентификатор дела' in tr_text:
                case_info['uid'] = val
            if 'Дата поступления' in tr_text:
                case_info['entry_date'] = val
            if 'Номер протокола об АП' in tr_text:
                case_info['protocol_number'] = val
            if 'Судья' in tr_text:
                case_info['judge'] = val
            if 'Дата рассмотрения' in tr_text:
                case_info['result_date'] = val
            if 'Результат рассмотрения' in tr_text:
                case_info['result'] = val

        print(case_info)

        return case_info


class SecondParser(CourtSiteParser):

    def get_pages_number(self, page):
        pagination = page.find('ul', class_='pagination')
        if pagination:
            return pagination.findAll('li')[-1]
        else:
            return 1

    def get_cases_urls(self, page):
        urls = []

        a_cases = page.findAll('a', class_='open-lawcase')
        for a in a_cases:
            urls.append(a['href'] + '&nc=1')
        return urls

    def get_case_information(self, url):

        case_info = {}
        txt = self.send_get_request(url)
        page = BeautifulSoup(txt, 'html.parser')
        case_trs = page.find('div', id='tab_content_Case').findAll('tr')
        for tr in case_trs:
            tr_text = tr.text
            val = tr.findAll('td')[1].text
            if 'Уникальный идентификатор дела' in tr_text:
                case_info['uid'] = val
            if 'Дата поступления' in tr_text:
                case_info['entry_date'] = val
            if 'Номер протокола об АП' in tr_text:
                case_info['protocol_number'] = val
            if 'Судья' in tr_text:
                case_info['judge'] = val
            if 'Дата рассмотрения' in tr_text:
                case_info['result_date'] = val
            if 'Результат рассмотрения' in tr_text:
                case_info['result'] = val

        print(case_info)

        return case_info


first_rf_parser = FirstParser()
second_rf_parser = SecondParser()


class RFCasesParser(CommonParser):

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

    def generate_url(self, court, params):
        site_type = str(court.site_type)
        string = self.site_params[site_type]['string']
        params_dict = self.site_params[site_type]['params_dict']
        return court.url + self.generate_params(string, params_dict, params)

    def get_cases_first_instance(self):
        articles = CodexArticle.objects.filter(codex=self.codex)
        article_string = self.generate_articles_string(articles)
        print(article_string)
        for court in Court.objects.all()[:5]:
            params = {'articles': article_string}
            url = self.generate_url(court, params)
            if court.site_type == 2:
                url = url.replace('XXX', court.vn_kod)
                second_rf_parser.get_cases(url)
            elif court.site_type == 1:
                first_rf_parser.get_cases(url)
