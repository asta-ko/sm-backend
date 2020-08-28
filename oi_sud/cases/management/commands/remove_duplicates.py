from django.core.management.base import BaseCommand
from oi_sud.cases.models import Case
from oi_sud.cases.updater import merger_updater


class Command(BaseCommand):

    def handle(self, *args, **options):
        cases = Case.duplicates.all()
        print(cases.count())
        count = 0
        for case in cases:
            merger_updater.process_duplicates(case)
            count += 1
            if count % 100 == 0:
                print(count)
