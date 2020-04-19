from django.core.management.base import BaseCommand

from oi_sud.cases.models import Case


class Command(BaseCommand):

    # def add_arguments(self, parser):
    #     parser.add_argument('region')

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        # courts = Court.objects.filter(site_type=2)
        # region = options['region']

        cases = Case.objects.filter(court__region=77, result_text__isnull=False)

        for case in cases:
            print(case.id)
            print(case.defendants.all()[0])
            case.update_case()
