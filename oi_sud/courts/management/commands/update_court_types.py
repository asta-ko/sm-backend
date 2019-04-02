from django.core.management.base import BaseCommand

from oi_sud.courts.parser import courts_parser
from oi_sud.courts.models import Court

class Command(BaseCommand):

    def handle(self, *args, **options):
        for court in Court.objects.all():
            c_type, instance = courts_parser.get_court_type(court.title)
            court.type = c_type
            court.instance = instance
            court.save()