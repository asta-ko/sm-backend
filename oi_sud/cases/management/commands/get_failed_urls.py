import json

from django.core.management.base import BaseCommand
from django_celery_results.models import TaskResult


class Command(BaseCommand):

    def handle(self, *args, **options):
        all_urls = []
        results = TaskResult.objects.filter(task_name='oi_sud.cases.tasks.get_koap_cases_first', result__isnull=False)
        for item in results:
            result_dict = json.loads(item.result)
            for court in result_dict.values():
                if court.get('error_urls') and len(court.get('error_urls')) > 0:
                    # for url in court.get('error_urls'):
                    #     print(url)
                    url = court.get('error_urls')[0]
                    print(url)
                    all_urls.append(url)
