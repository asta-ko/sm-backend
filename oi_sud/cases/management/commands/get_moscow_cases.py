from django.core.management.base import BaseCommand

from oi_sud.cases.parsers.moscow import MoscowCasesGetter


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('codex', type=str,
                            help='Кодекс: koap - кодекс об АП, uk - уголовный. Обязательный параметр')
        parser.add_argument('instance', type=int, help='Инстанция: 1 - первая, 2 - вторая. Обязательный параметр')
        parser.add_argument(
            '--entry_date_from',
            type=str,
            help='Дата поступления дела, с которой начинаем забирать дела, в формате DD.MM.YYYY. Необязательный параметр'
        )

        parser.add_argument(
            '--articles',
            type=str,
            help='Статьи, по которым забираем дела в формате "19.3 ч.1, 20.2 ч.5, 20.2 ч.8" (в кавычках). Необязательный параметр'
        )

    def handle(self, *args, **options):
        codex = options['codex']
        instance = options['instance']
        entry_date_from = options.get('entry_date_from')  # DD.MM.YYYY
        articles = options.get('articles')  # 19.3 ч.1, 20.2 ч.5, 20.2 ч.8
        articles_list = None if not articles else articles.split(', ')
        MoscowCasesGetter().get_cases(instance, codex, entry_date_from=entry_date_from, articles_list=articles_list)
