from django.core.management.base import BaseCommand
from django.db.models import Count

from oi_sud.cases.models import Case


class Command(BaseCommand):

    def handle(self, *args, **options):
        cases = Case.objects.all().annotate(num_defendants=Count('defendants')).filter(court__region=78,
                                                                                       court__site_type=1,
                                                                                       num_defendants__gt=1, type=1)
        for case in cases[:25]:
            case.update_case()
            advocates_names = [x.name_normalized for x in case.get_advocates()]
            if advocates_names:
                for defense in case.defenses.all():
                    if defense.defendant.name_normalized in advocates_names:
                        defense.delete()
