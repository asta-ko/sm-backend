from django.core.management.base import BaseCommand
from oi_sud.cases.tasks import update_risk_group


class Command(BaseCommand):

    def handle(self, *args, **options):
        update_risk_group()
