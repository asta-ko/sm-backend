from chunkator import chunkator
from django.core.management.base import BaseCommand
from oi_sud.cases.models import Case, CasePenalty


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('init...')

        CasePenalty.objects.all().delete()

        count = 0
        for case in chunkator(Case.objects.filter(result_text__isnull=False, type=1, stage=1), 100):
            count += 1
            if count == 1:
                print('started...')
            if not case.penalties.count():
                case.process_result_text()
            if count % 100 == 0:
                print(count)
            if count > 500:  # здесь определяем число дел, которые обрабатываем
                break

        # print(Case.objects.filter(result_text__isnull=False, type=1).count(), 'case number count')
        print(CasePenalty.objects.count(), 'all penalties count')
        print(CasePenalty.objects.exclude(type__in=['error', 'no_data']).count(), 'ok penalties')
        print(CasePenalty.objects.filter(type='error').count(), 'error penalties')
        print(CasePenalty.objects.filter(type='no_data').count(), 'could not process penalties')
        print(CasePenalty.objects.filter(type='caution').count(), 'caution penalties')
