from django.core.management.base import BaseCommand
from oi_sud.cases.models import Defendant, Case
from django.db.models import Count

class Command(BaseCommand):

    def handle(self, *args, **options):
        groups = []
        s = Defendant.objects.values('name_normalized').order_by('name_normalized').annotate(the_count=Count('name_normalized'))
        for x in s:
            if x['the_count'] > 1:
                print(x)
                print([x.name for x in Defendant.objects.filter(name_normalized=x['name_normalized'])])
                defendants = Defendant.objects.filter(name_normalized=x['name_normalized'])
                names_dict = {}
                duplicate_names_dict = {}
                for x in defendants:
                    ntuple = (x.last_name, x.first_name, x.middle_name)
                    if not names_dict.get(ntuple):
                        names_dict[ntuple] = []
                    names_dict[ntuple].append(x.id)
                for v in names_dict.values():
                    if len(v) > 1:
                        first_defendant = Defendant.objects.get(id=v[0])
                        next_defendants = Defendant.objects.filter(id__in=v[1:])
                        for d in next_defendants:
                            for c in d.defenses.all():
                                c.defendant = first_defendant
                                c.save()
                            d.delete()



