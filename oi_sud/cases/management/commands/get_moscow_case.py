from django.core.management.base import BaseCommand
from oi_sud.cases.parsers.moscow import MoscowCasesGetter, MoscowParser

class Command(BaseCommand):

    def handle(self, *args, **options):
        url = 'https://mos-gorsud.ru/rs/tverskoj/services/cases/admin/details/c694e8b1-d345-4933-af40-25a3ad4ba819?documentMainArticle=%D1%81%D1%82.+19.34%2C+%D0%A7.2&formType=fullForm'
        case_info = MoscowParser().get_raw_case_information(url)
        #MoscowCasesGetter(codex='koap').get_cases(1, articles_list=['19.34 ч.2'])

