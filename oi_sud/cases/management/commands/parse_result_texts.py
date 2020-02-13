from django.core.management.base import BaseCommand

from oi_sud.cases.models import Case, CasePenalty


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('starting')
        count = 0

        cases = Case.objects.filter(result_text__isnull=False, type=1)#[10000:35000]
        print(cases.count())
        for case in cases:
            count += 1

            try:
                if not case.penalties.count():
                    case.process_result_text()
            except:
                raise
                print('error', case.get_admin_url())
            if count % 1000 == 0:
                print(count)
        print(CasePenalty.objects.count())
        print(CasePenalty.objects.all())
