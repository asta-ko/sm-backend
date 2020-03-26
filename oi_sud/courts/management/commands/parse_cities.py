from django.core.management.base import BaseCommand
from oi_sud.core.utils import get_city_from_address
from oi_sud.courts.models import Court


class Command(BaseCommand):

    def handle(self, *args, **options):
        errored = []
        for court in Court.objects.all():
            city = get_city_from_address(court.full_address)
            court.city = city
            court.save()
            print(city)
            if not city:
                errored.append(court.full_address)
        print('===========================================================')
        print(errored)
