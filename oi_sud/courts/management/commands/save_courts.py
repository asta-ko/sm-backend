from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court
from oi_sud.courts.parser import courts_parser


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        courts_parser.save_courts()
