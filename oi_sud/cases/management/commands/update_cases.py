from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court
from oi_sud.cases.updater import  CasesUpdater

class Command(BaseCommand):

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        #courts = Court.objects.filter(site_type=2)
        CasesUpdater(codex='koap').update_cases()

