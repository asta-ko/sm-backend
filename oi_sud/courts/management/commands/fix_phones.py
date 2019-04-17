import re
from django.core.management.base import BaseCommand
from oi_sud.courts.models import Court


class Command(BaseCommand):

    def handle(self, *args, **options):
        errored = []
        for court in Court.objects.all():
            phone_numbers = court.phone_numbers
            for phone in phone_numbers:
                m = re.search(r'\(\d+\)\(\d+\)', phone)
                if m:
                    phone_numbers.remove(phone)
                    court.phone_numbers = phone_numbers
                    court.save()
                    print(court.phone_numbers)

        print('===========================================================')
        print(errored)




