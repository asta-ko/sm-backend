from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court
from oi_sud.cases.parsers.rf import RFCasesGetter, FirstParser

class Command(BaseCommand):

    def handle(self, *args, **options):

        urls=['https://sunja--ing.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=4202034&delo_id=1500001&hide_parts=0']

        #RFCasesGetter(codex='koap').save_cases(urls=urls)
        FirstParser(court=None, stage=1, codex='koap', url=None).save_cases(urls=urls)