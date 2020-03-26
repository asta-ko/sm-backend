from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court


class Command(BaseCommand):

    def handle(self, *args, **options):
        courts = Court.objects.filter(case__isnull=True)
        for court in courts:
            print(court.title, court.url)
