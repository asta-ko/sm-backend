from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court
from oi_sud.cases.parser import RFCasesParser

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('codex', type=str)
        parser.add_argument('instance', type=int)
        parser.add_argument(
            '--region',
        )

        parser.add_argument(
            '--limit',
            type=int
        )

        parser.add_argument(
            '--entry_date_from',
            type=str
        )

    def handle(self, *args, **options):
        courts = Court.objects.filter(instance=1)
        limit = None
        entry_date_from = None
        codex = options['codex']
        instance = options['instance']
        if options.get('region'):
            region = options['region']
            courts = courts.filter(region=region)
        if options.get('limit'):
            limit = options['limit']
        if options.get('entry_date_from'): #DD.MM.YYYY
            entry_date_from = options['entry_date_from']

        RFCasesParser(codex=codex).get_cases(instance, courts=courts, courts_limit=limit, entry_date_from=entry_date_from)