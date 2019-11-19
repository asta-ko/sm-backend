import pytz
from django.contrib.postgres.fields import ArrayField
from django.db import models

from oi_sud.core.consts import region_choices
from oi_sud.core.utils import nullable

from oi_sud.core.consts import region_choices, timezone_dict, far_east_timezone_dict

COURT_TYPES = (
    (0, 'Районный суд'),
    (1, 'Городской суд'),
    (2, 'Городской суд (федерального значения)'),
    (3, 'Областной суд'),
    (4, 'Краевой суд'),
    (5, 'Гарнизонный военный суд'),
    (6, 'Окружной военный (флотский) суд'),
    (7, 'Суд автономного округа'),
    (8, 'Суд автономной области'),
    (9, 'Участок мирового судьи')
)

COURT_INSTANCE_TYPES = (
    (1, 'Суд первой инстанции'),
    (2, 'Суд второй инстанции')
)

SITE_TYPES = (
    (1, 'Первый тип сайта'),
    (2, 'Второй тип сайта'),
    (3, 'Московский тип сайта'),
    (4, 'Мировой суд - тип msudrf')
)


class Judge(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    court = models.ForeignKey('Court', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Судья'
        verbose_name_plural = 'Судьи'

    @staticmethod
    def autocomplete_search_fields():
        return 'name',


def new_array():
    return []

class Court(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название', db_index=True)
    phone_numbers = ArrayField(models.CharField(max_length=25, blank=True), verbose_name='Телефоны')
    full_address = models.CharField(max_length=200, verbose_name='Адрес', **nullable)
    city = models.CharField(max_length=50, verbose_name='Населенный пункт', **nullable)
    region = models.IntegerField(verbose_name='Регион', choices=region_choices)
    url = models.URLField(verbose_name='URL', **nullable)
    type = models.IntegerField(verbose_name='Тип суда', choices=COURT_TYPES)  # районный/областной/военный/городской
    instance = models.IntegerField(verbose_name='Тип суда по инстанции', choices=COURT_INSTANCE_TYPES, default=1)
    site_type = models.IntegerField(verbose_name='Тип сайта суда', choices=SITE_TYPES, default=1)  # тип сайта для парсинга
    vn_kod = models.CharField(verbose_name='VN код', max_length=25, **nullable) #для 2 типа сайтов
    email = models.CharField(verbose_name='Email', max_length=40, **nullable)
    not_available = models.BooleanField(default=False)
    servers_num = models.IntegerField(verbose_name='Количество серверов', null=True, blank=True, default=1) #для 1 и 2 типа сайтов
    unprocessed_cases_urls = ArrayField(models.CharField(max_length=200), default=new_array, blank=True, verbose_name='Дела для обработки')

    class Meta:
        verbose_name = 'Суд'
        verbose_name_plural = 'Суды'

    @staticmethod
    def autocomplete_search_fields():
        return 'title',


    def __str__(self):
        return self.title

    # def get_


    def get_timezone(self):
        r = {y: x for x, y in dict(region_choices).items()}
        if self.region != r['Республика Саха (Якутия)'] and self.city != 'г. Северо-Курильск':
            for timezone in timezone_dict.keys():
                if self.region in timezone_dict[timezone]:
                    return pytz.timezone(timezone)
        else:
            for timezone in far_east_timezone_dict.keys():
                if self.city in far_east_timezone_dict[timezone]:
                    return pytz.timezone(timezone)