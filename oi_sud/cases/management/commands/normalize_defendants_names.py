from django.core.management.base import BaseCommand
from oi_sud.cases.models import Defendant
from oi_sud.cases.utils import parse_name_and_get_gender
class Command(BaseCommand):

    def handle(self, *args, **options):
        for d in Defendant.objects.all():
            normalized_name = d.normalize_name()
            if d.name != normalized_name or not d.name_normalized:
                #print(d.name, normalized_name)
                d.name_normalized = normalized_name
                d.save()
            names, gender = parse_name_and_get_gender(d.name)
            print(names, gender)
            if gender:
                d.gender = gender
            if len(names):
                d.last_name = names[0]
                d.first_name = names[1]
                d.middle_name = names[2]
            d.save()

