from django.core.management.base import BaseCommand
from oi_sud.cases.models import Case
from oi_sud.cases.consts import EVENT_TYPES, EVENT_RESULT_TYPES, RESULT_TYPES, APPEAL_RESULT_TYPES

event_types_dict = dict(EVENT_TYPES)
event_result_types_dict = dict(EVENT_RESULT_TYPES)
result_types_dict = dict(RESULT_TYPES)
appeal_result_types_dict = dict(APPEAL_RESULT_TYPES)




class Command(BaseCommand):

    def handle(self, *args, **options):
        n = 0
        r_types = [str(x) for x in  list(result_types_dict.keys())]
        print(Case.objects.filter(result_type__in=r_types).count())
        while Case.objects.filter(result_type__in=r_types).count() != 0:
            for case in Case.objects.filter(result_type__in=r_types)[:3000]:
                n +=1
                if case.result_type and len(case.result_type)<4:
                    case.result_type = result_types_dict[int(case.result_type)]
                    case.save()
                    #print(case.id)
                if case.appeal_result and len(case.appeal_result)<3:
                    case.appeal_result = appeal_result_types_dict[int(case.appeal_result)]
                    case.save()
                for event in case.events.all():
                    if len(event.type)<4:
                        event.type = event_types_dict[int(event.type)]
                    if event.result and len(event.result)< 3:
                        event.result = event_result_types_dict[int(event.result)]
                    event.save()

                if n % 1000 == 0:
                    print(n)
