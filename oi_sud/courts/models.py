from django.contrib.postgres.fields import ArrayField
from django.db import models

from oi_sud.core.consts import region_choices
from oi_sud.core.utils import nullable

COURT_TYPES = (
    (0, 'Районный суд'),
    (1, 'Городской суд'),
    (2, 'Городской суд (федерального значения)'),
    (3, 'Областной суд'),
    (4, 'Краевой суд'),
    (5, 'Гарнизонный военный суд'),
    (6, 'Окружной военный (флотский) суд'),
    (7, 'Суд автономного округа'),
    (8, 'Суд автономной области')
)

COURT_INSTANCE_TYPES = (
    (1, 'Суд первой инстанции'),
    (2, 'Суд второй инстанции')
)

SITE_TYPES = (
    (1, 'Первый тип сайта'),
    (2, 'Второй тип сайта'),
    (3, 'Московский тип сайта')
)


class Judge(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    court = models.ForeignKey('Court', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Court(models.Model):
    title = models.CharField(max_length=100)
    phone_numbers = ArrayField(models.CharField(max_length=25, blank=True), )
    full_address = models.CharField(max_length=200, **nullable)
    city = models.CharField(max_length=50, **nullable)
    region = models.IntegerField(choices=region_choices)
    url = models.URLField(null=True, blank=True)
    type = models.IntegerField(choices=COURT_TYPES)  # районный/областной/военный/городской
    instance = models.IntegerField(choices=COURT_INSTANCE_TYPES, default=1)
    site_type = models.IntegerField(choices=SITE_TYPES, default=1)  # тип сайта для парсинга
    vn_kod = models.CharField(max_length=25, **nullable)
    email = models.CharField(max_length=40, **nullable)

    def __str__(self):
        return self.title
