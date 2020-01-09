from django.core.management.base import BaseCommand
from oi_sud.cases.parsers.moscow import MoscowCasesGetter, MoscowParser

class Command(BaseCommand):

    def handle(self, *args, **options):
        url = 'https://mos-gorsud.ru/rs/hamovnicheskij/services/cases/admin/details/a816fe67-4956-4b9c-9399-ea3908161023?documentMainArticle=%D0%A1%D1%82.+20.2%2C+%D0%A7.2&formType=fullForm'
        #url = 'https://mos-gorsud.ru/rs/zamoskvoreckij/services/cases/criminal/details/9ec54f94-417e-4107-b8d0-20f21852cb45?participantArticle=%D0%A1%D1%82.+212%2C+%D0%A7.+2&formType=fullForm'
        #url = 'https://mos-gorsud.ru/rs/meshchanskij/services/cases/admin/details/013d44b3-b076-44d0-a813-d9ea71cd1539?documentMainArticle=%D0%A1%D1%82.+19.34%2C+%D0%A7.2&formType=fullForm'#'https://mos-gorsud.ru/rs/tverskoj/services/cases/admin/details/c694e8b1-d345-4933-af40-25a3ad4ba819?documentMainArticle=%D1%81%D1%82.+19.34%2C+%D0%A7.2&formType=fullForm'
        #case_info = MoscowParser(codex='uk').get_raw_case_information(url)
        #print(case_info)
        #MoscowParser(codex='uk').serialize_data(case_info)
        case = MoscowParser(stage=1, codex='koap').save_cases(urls=[url])
        #print(case_info)
        #MoscowCasesGetter().get_cases(1, 'koap', articles_list=['20.2 ч.8', '19.34 ч.2'])

