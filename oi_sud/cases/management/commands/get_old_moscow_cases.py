from django.core.management.base import BaseCommand
from oi_sud.cases.parsers.rf import RFCasesGetter
from oi_sud.courts.models import Court

# для старых московских судов


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('codex', type=str)
        parser.add_argument('instance', type=int)
        # parser.add_argument(
        #     '--region',
        # )
        #
        # parser.add_argument(
        #     '--limit',
        #     type=int
        # )
        #
        # parser.add_argument(
        #     '--entry_date_from',
        #     type=str
        # )

    def handle(self, *args, **options):
        courts = Court.objects.filter(region=77, site_type=2)

        codex = options['codex']
        instance = options['instance']

        courts_ids = courts.values_list('id', flat=True)

        RFCasesGetter(codex=codex).get_cases(instance, courts_ids=courts_ids)
