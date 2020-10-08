from django.core.management.base import BaseCommand
from django.db.models import Count

from oi_sud.cases.models import Case


class Command(BaseCommand):

    def handle(self, *args, **options):
        cases = Case.objects.all().annotate(num_defendants=Count('defendants')).filter(codex_articles__isnull=True)
        print([x.url for x in cases[:20]])
        print(cases.count())
       # cases.delete()
#for case in cases:
            #case.update_case()
            #advocates_names = [x.name_normalized for x in case.get_advocates()]
            #if advocates_names:
            #    for defense in case.defenses.all():
            #        if defense.defendant.name_normalized in advocates_names:
            #            print(defense, 'defense_to_delet')
            #            defense.delete()
