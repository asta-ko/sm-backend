from chunkator import chunkator
from django.core.management.base import BaseCommand
from django.utils import timezone
from oi_sud.cases.models import Case, CasePenalty
from oi_sud.core.consts import region_choices


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('init...')
        for region in region_choices:

            # CasePenalty.objects.filter(case__court__region=region[0]).delete()

            count = 0
            for case in chunkator(Case.objects.filter(court__region=region[0], penalties__isnull=True,
                                                      result_text__isnull=False, type=1, stage=1), 100):
                count += 1
                if count == 1:
                    print(f'started...')
                if not case.penalties.count():
                    case.process_result_text()
                if count % 100 == 0:
                    print(count, region[1])
                # if count > 2000:  # здесь определяем число дел, которые обрабатываем
                #     break
            print(f'Ended {region[1]}')

        print(CasePenalty.objects.count(), 'all penalties count')
        print(CasePenalty.objects.exclude(type__in=['error', 'no_data']).count(), 'ok penalties')
        for x in ['fine', 'works', 'arrest', 'error', 'no_data', 'caution', 'suspension']:
            text = x if x != 'no_data' else 'could not process'
            print(CasePenalty.objects.filter(type=x).count(), f'{text} penalties')

        with open(f'parse_texts_log_{timezone.now()}.txt', 'a') as f:
            print(CasePenalty.objects.count(), 'all penalties count', file=f)
            print(CasePenalty.objects.exclude(type__in=['error', 'no_data']).count(), 'ok penalties', file=f)
            for x in ['fine', 'works', 'arrest', 'error', 'no_data', 'caution', 'suspension']:
                text = x if x != 'no_data' else 'could not process'
                print(CasePenalty.objects.filter(type=x).count(), f'{text} penalties', file=f)

            print('\n\nCOULD NOT PROCESS\n\n**************************\n\n', file=f)
            for cp in CasePenalty.objects.filter(type='no_data'):
                print(cp.case.get_result_text_resolution(), file=f)
                print(cp.case.get_result_text_url(), file=f)
                print('_________________________________', file=f)
