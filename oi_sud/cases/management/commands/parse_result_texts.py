from chunkator import chunkator
from django.core.management.base import BaseCommand
from oi_sud.cases.models import Case, CasePenalty


class Command(BaseCommand):

    def handle(self, *args, **options):

        CasePenalty.objects.all().delete()
        print('starting')
        count = 0

        for case in chunkator(Case.objects.filter(result_text__isnull=False, type=1), 200):
            count += 1
            try:
                if not case.penalties.count():
                    case.process_result_text()
            except Exception as e:
                print('error', e, case.get_admin_url())
                # raise
            if count % 1000 == 0:
                print(count)

        print(Case.objects.filter(result_text__isnull=False, type=1).count(), 'case number count')
        print(CasePenalty.objects.count(), 'all penalties count')
        print(CasePenalty.objects.filter(type='error').count(), 'error penalties')
