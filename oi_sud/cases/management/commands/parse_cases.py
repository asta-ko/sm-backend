from django.core.management.base import BaseCommand

from oi_sud.cases.parsers.rf import FirstParser


class Command(BaseCommand):

    def handle(self, *args, **options):
        urls = [
            'https://muhorshibirsky--bur.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=34508304&case_uid=49e857f5-f597-4686-aa0a-3cadd78ff2dd&delo_id=1500001']

        # urls=['https://ordjonikidzovsky--bkr.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=527375399&delo_id=1500001']
        # urls=['https://birsky--bkr.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=470082934&delo_id=1500001']
        # RFCasesGetter(codex='koap').save_cases(urls=urls)
        FirstParser(court=None, stage=1, codex='koap', url=None).save_cases(urls=urls)
