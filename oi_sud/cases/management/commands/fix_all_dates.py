from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import F
from oi_sud.cases.models import Case


class Command(BaseCommand):

    def handle(self, *args, **options):
        cases = Case.objects.all()
        for d in ['entry_date', 'result_date', 'result_published_date', 'result_valid_date',
                  'forwarding_to_higher_court_date', 'forwarding_to_lower_court_date', 'appeal_date']:
            filter = {f'{d}__isnull': False}
            update = {d: F(d) + timedelta(days=1)}
            cases.filter(**filter).update(**update)
