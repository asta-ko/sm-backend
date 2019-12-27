from django.core.management.base import BaseCommand

from oi_sud.cases.models import Case, CasePenalty


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('starting')

        cases = Case.objects.filter(result_text__isnull=False, type=1)
        print(cases.count())
        for case in cases:

            try:
                if not case.penalties.count():
                    case.process_result_text()
            except:
                print('error', case.get_admin_url())
        print(CasePenalty.objects.count())
        print(CasePenalty.objects.all())
