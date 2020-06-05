from chunkator import chunkator
from django.core.management.base import BaseCommand
from oi_sud.cases.models import Defendant


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('init...')

        count = 0

        d = Defendant.objects.filter(first_name__isnull=False)

        for defendant in chunkator(d, 100):
            count += 1
            if count == 1:
                print('started...')

            defendant.gender = defendant.get_gender()
            defendant.save()

            if count % 100 == 0:
                print(count)

            if count > 250:  # здесь определяем число дел, которые обрабатываем
                break
