from chunkator import chunkator
from django.core.management.base import BaseCommand
from oi_sud.cases.models import Case


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('init...')

        print(Case.objects.filter(result_date__isnull=True))

        result_events_titles = ['Рассмотрение дела по существу',
                                'Судебное заседание для решения вопроса об избрании/продлении меры пресечения',
                                'Решение в отношении поступившего уголовного дела', 'Судебное заседание']
        count = 0
        for case in chunkator(
                Case.objects.filter(events__title__in=result_events_titles, result_date__isnull=True, type=1, stage=1),
                100):
            count += 1
            if count == 1:
                print('started...')

            date = case.events.filter(title__in=result_events_titles).last().date
            case.result_date = date
            case.save()
            if count % 100 == 0:
                print(count)
            if count > 500:  # здесь определяем число дел, которые обрабатываем
                break

        print(Case.objects.filter(result_date__isnull=True))
