from chunkator import chunkator
from django.core.management.base import BaseCommand
from oi_sud.cases.models import Case
from oi_sud.core.consts import region_choices


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('init...')
        print(Case.objects.filter(penalties__isnull=False, result_type__isnull=True, stage=1, type=1).count())

        for region in region_choices:

            count = 0
            for case in chunkator(
                    Case.objects.filter(court__region=region[0], penalties__isnull=False, result_type__isnull=True,
                                        stage=1, type=1), 100):
                count += 1
                case.result_type = 'Вынесено постановление о назначении административного наказания'
                case.save()

                if count % 100 == 0:
                    print(count)
            print(f'Ended {region[1]}')
