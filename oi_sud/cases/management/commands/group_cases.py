from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court
from oi_sud.cases.grouper import  grouper

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('region', type=int)
        parser.add_argument('codex', type=str)

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        #courts = Court.objects.filter(site_type=2)
        region = options['region']
        codex = options['codex']
        if codex not in ['uk', 'koap']:
            print('Codex is not uk and not koap. Exiting.')
            return
        grouper.group_cases(region=region)