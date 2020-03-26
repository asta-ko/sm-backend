from django.core.management.base import BaseCommand

from oi_sud.cases.models import Case


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('region', type=int)

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        # courts = Court.objects.filter(site_type=2)
        region = options['region']

        cases = Case.objects.filter(court__region=region)
        for case in cases:
            case.update_case()
