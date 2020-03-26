from django.core.management.base import BaseCommand
from oi_sud.cases.parsers.rf import RFCasesGetter
from oi_sud.courts.models import Court


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        courts = Court.objects.filter(site_type=2, region=78)
        courts_ids = courts.values_list('id', flat=True)
        RFCasesGetter(codex='koap').get_cases(1, courts_ids=courts_ids, courts_limit=5)
