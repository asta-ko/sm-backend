from django.core.management.base import BaseCommand

from oi_sud.courts.parser import moscow_courts_parser


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        moscow_courts_parser.save_courts()
