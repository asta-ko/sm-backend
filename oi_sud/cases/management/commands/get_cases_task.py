from django.core.management.base import BaseCommand
from oi_sud.cases.tasks import main_get_koap_cases


class Command(BaseCommand):

    def handle(self, *args, **options):
        main_get_koap_cases.delay()
