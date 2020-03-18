from django.core.management.base import BaseCommand
from oi_sud.cases.parsers.moscow import MoscowParser
from oi_sud.cases.parsers.rf import RFCourtSiteParser


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('type', type=str, help='Принимает значения moscow или rf. Обязательный параметр.')
        parser.add_argument('urls', type=str, help='Принимает список урлов в формате "https://mos-gorsud.ru/rs/hamovnicheskij/services/cases/admin/details/a816fe67-4956-4b9c-9399-ea3908161023, https://mos-gorsud.ru/rs/zamoskvoreckij/services/cases/criminal/details/9ec54f94-417e-4107-b8d0-20f21852cb45" (в кавычках). Обязательный параметр.')

    def handle(self, *args, **options):

        urls_list = options['urls'].split(', ')
        if not urls_list:
            print('Got no urls')
            return

        parser_type = options['type']
        if not parser_type in ['rf', 'moscow']:
            print('Please specify rf or moscow')
            return

        if parser_type == 'moscow':
            MoscowParser(stage=1, codex='koap').save_cases(urls=urls_list)
        elif parser_type == 'rf':
            #TODO: get court from url, then use first or second parser
            print('Not implemented yet')
            return
