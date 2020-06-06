from django.core.management.base import BaseCommand
from oi_sud.cases.parsers.rf import RFCasesGetter
from oi_sud.courts.models import Court


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        # courts = Court.objects.filter(id=2232)
        # courts_ids = courts.values_list('id', flat=True)
        RFCasesGetter(codex='koap').get_cases(1, courts_ids=[2232,], courts_limit=1)
