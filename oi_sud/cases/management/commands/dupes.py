
from django.core.management.base import BaseCommand

from oi_sud.cases.models import Case
from django.db.models import Count

class Command(BaseCommand):

    def handle(self, *args, **options):
        dupes = Case.objects.values('case_uid', 'case_number', 'court').annotate(Count('id')).order_by().filter(id__count__gt=1)
        print(dupes)
        print(len(dupes))
        n = 0
        for dup in dupes:
            cases = Case.objects.filter(case_uid=dup['case_uid'], case_number=dup['case_number'], court__id=dup['court']).order_by('-created_at')
            latest = cases.first()
            cases.exclude(id=latest.id).delete()
            n += 1
            if n%1000==0:
                print(n)
