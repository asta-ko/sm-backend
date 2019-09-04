from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court
from oi_sud.cases.parsers.rf import RFCasesGetter

class Command(BaseCommand):

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        courts = Court.objects.filter(site_type=2)
        RFCasesGetter(codex='uk').get_cases(2, courts=courts, courts_limit=5)

