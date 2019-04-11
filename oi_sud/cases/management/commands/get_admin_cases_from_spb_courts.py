from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court
from oi_sud.cases.parser import RFCasesParser

class Command(BaseCommand):

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        courts = Court.objects.filter(region=81)
        RFCasesParser(codex='koap').get_cases_first_instance(courts=courts, courts_limit=5)

