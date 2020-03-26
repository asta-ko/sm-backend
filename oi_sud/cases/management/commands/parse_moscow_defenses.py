from django.core.management.base import BaseCommand
from oi_sud.cases.parsers.moscow import MoscowParser


class Command(BaseCommand):

    def handle(self, *args, **options):
        s = 'Гаврилов С.В. (Ст. 282.1, Ч. 2; Ст. 282.1, Ч. 1), Дубовик М.С. (Ст. 282.1, Ч. 1; Ст. 282.1, Ч. 2), Карамзин П.А. (Ст. 282.1, Ч. 2; Ст. 282.1, Ч. 1), Костыленков Р.Д. (Ст. 282.1, Ч. 2; Ст. 282.1, Ч. 1), Крюков В.В. (Ст. 282.1, Ч. 1; Ст. 282.1, Ч. 2), Павликова А.Д. (Ст. 282.1, Ч. 1; Ст. 282.1, Ч. 2), Полетаев Д.В. (Ст. 282.1, Ч. 1; Ст. 282.1, Ч. 2), Рощин М.В. (Ст. 282.1, Ч. 2; Ст. 282.1, Ч. 1)'
        MoscowParser().get_uk_defenses(s)
