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

    def get_pages_number(self, page):

        pagination_a = page.find('a', attrs={'title':'На последнюю страницу списка'})
        if not pagination_a:
            return 1
        else:
            last_page_href=pagination_a['href']
            pages_number = int(get_query_key(last_page_href, 'page'))
            return pages_number

    def parse_case_table(self):
        pass

    def get_cases(self, url):
        r = self.send_get_request(url)
        txt = self.send_get_request(url)
        page = BeautifulSoup(txt, 'html.parser')
        pages_number=self.get_pages_number(page)

    def get_cases_first_instance(self):
        articles = CodexArticle.objects.filter(codex=self.codex)
        article_string = self.generate_articles_string(articles)
        print(article_string)
        for court in Court.objects.all()[:5]:
            params = {'articles':article_string}
            url = self.generate_url(court, params)
            if court.site_type==2:
                url.replace('XXX', court.vn_kod)
            print(url)
            self.get_cases(url)



