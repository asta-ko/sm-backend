from django.core.management.base import BaseCommand
from oi_sud.cases.parsers.rf import RFCasesGetter
from oi_sud.courts.models import Court


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('codex', type=str,
                            help='Кодекс: koap - кодекс об АП, uk - уголовный. Обязательный параметр')
        parser.add_argument('instance', type=int, help='Инстанция: 1 - первая, 2 - вторая. Обязательный параметр')
        parser.add_argument(
            '--region',
            help='Регион судов. Номера можно посмотреть в core/consts. Необязательный параметр.'
        )

        parser.add_argument(
            '--limit',
            type=int, help='Максимальное количество судов, из которых забираем дела. Необязательный параметр'
        )

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
        courts = Court.objects.filter(instance=1)

        codex = options['codex']
        instance = options['instance']
        if options.get('region'):
            region = options['region']
            courts = courts.filter(region=region)

        limit = options.get('limit')
        entry_date_from = options.get('entry_date_from')  # DD.MM.YYYY
        articles = options.get('articles')  # 19.3 ч.1, 20.2 ч.5, 20.2 ч.8

        courts_ids = courts.values_list('id', flat=True)

        RFCasesGetter(codex=codex).get_cases(instance, courts_ids=courts_ids, courts_limit=limit,
                                             entry_date_from=entry_date_from, custom_articles=articles)
