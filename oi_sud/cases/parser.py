from oi_sud.core.parser import CommonParser
from .consts import site_type_dict, site_types_by_codex

# class OldCasesParser(CommonParser):
#     pass
#
# class MoscowNewCasesParser(CommonParser):
#     pass
#
# class MJudgesCasesParser(CommonParser):
#     pass


class RFSitesParamGenerator(object):




rf_url_generator = RFSitesParamGenerator()

class RFCasesParser(CommonParser):

    def __init__(self, codex):
        self.codex = codex
        self.site_params = site_types_by_codex[self.codex]

    @staticmethod
    def generate_articles_string(articles):
        params_string = ''
        for article in articles:
            if article.part:
                params_string += f'&lawbookarticles[]={article.article_number}+.{article.part}'
            else:
                params_string += f'&lawbookarticles[]={article.article_number}'

        return params_string

    @staticmethod
    def generate_params(string, params_dict, params):
        result_string = ''
        result_string += string
        for k, v in params.items():
            if k in params_dict:
                result_string += '&{0}={1}'.format(params_dict[k], v)
        return result_string

    def generate_url(self, court, params):
        site_type = string(court.site_type)
        string = self.site_params[site_type]['string']
        params_dict = self.site_params[site_type]['params_dict']
        return court.url + self.generate_params(string, params_dict, params)

    def get_cases_first_instance(self):
        articles = CodexArticles.objects.filter(codex=self.codex)
        article_string = self.generate_articles_string(articles)
        for court in Courts.objects.all()[:5]:
            params = {'articles':article_string}
            url = self.generate_url(court, params)
            print(url)



