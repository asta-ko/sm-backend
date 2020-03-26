from django.core.management.base import BaseCommand

from oi_sud.cases.models import Case


class Command(BaseCommand):

    def handle(self, *args, **options):
        cases = Case.objects.filter(case_number__contains='ДЕЛО№')
        print(cases.count(), '...')
        for case in cases:
            case.case_number = case.case_number.replace('ДЕЛО№', '')
            case.save()
        cases = Case.objects.filter(case_number__contains='ДЕЛО№')
