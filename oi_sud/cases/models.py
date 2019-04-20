from django.db import models

from oi_sud.core.utils import nullable
from oi_sud.cases.consts import RESULT_TYPES, EVENT_TYPES, EVENT_RESULT_TYPES

CASE_TYPES = (
    (1, 'Дело об административном правонарушении'),
    (2, 'Уголовное дело'),
    (3, 'Производство по материалам')
)

CASE_STAGES = (
    (1, 'Первая инстанция'),
    (2, 'Аппеляция'),
    (3, 'Пересмотр')
)



GENDER_TYPES = ()


class Case(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entry_date = models.DateField(verbose_name='Дата поступления', db_index=True)  # поступление в суд
    result_date = models.DateField(verbose_name='Дата решения', **nullable)  # рассмотрение
    result_published = models.DateField(verbose_name='Дата публикации решения', **nullable)  # публикация решения
    result_valid = models.DateField(verbose_name='Решение вступило в силу', **nullable)  # решение вступило в силу
    judge = models.ForeignKey('courts.Judge', verbose_name='Судья',on_delete=models.CASCADE, **nullable)
    court = models.ForeignKey('courts.Court', verbose_name='Cуд', on_delete=models.CASCADE)
    defendants = models.ManyToManyField('Defendant', through='CaseDefense')
    advocates = models.ManyToManyField('Advocate', through='CaseDefense')
    case_number = models.CharField(max_length=50, verbose_name='Номер дела')  # Номер дела
    case_uid = models.CharField(max_length=50, verbose_name='ID в sudrf', **nullable)  # Уникальный id в системе sudrf
    protocol_number = models.CharField(max_length=50, verbose_name='Номер протокола', **nullable)  # номер протокола (для дел об АП)
    codex_articles = models.ManyToManyField('codex.CodexArticle', verbose_name='Статьи')
    result_type = models.IntegerField(choices=RESULT_TYPES, verbose_name='Решение по делу', **nullable)
    result_text = models.TextField(verbose_name='Текст решения', **nullable)  # Текст решения
    type = models.IntegerField(choices=CASE_TYPES, verbose_name='Тип судопроизводства')  # тип судопроизводства
    stage = models.IntegerField(choices=CASE_STAGES, verbose_name='Инстанция')  # первая инстанция, обжалование, пересмотр, кассация
    group = models.ForeignKey('CaseGroup', on_delete=models.CASCADE, **nullable)  # ссылки на аппеляции и пересмотры
    url = models.URLField(verbose_name='URL', unique=True, **nullable)

    class Meta:
        verbose_name = 'Дело'
        verbose_name_plural = 'Все дела'

    def __str__(self):
        articles_list = ','.join([str(x) for x in self.codex_articles.all()])
        return f'{self.case_number} {articles_list}'

class UKCase(Case):
    class Meta:
        proxy=True
        verbose_name = 'Дело (УК)'
        verbose_name_plural = 'Дела (УК)'

class KoapCase(Case):
    class Meta:
        proxy=True
        verbose_name = 'Дело (КОАП)'
        verbose_name_plural = 'Дела (КОАП)'

class CaseEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(verbose_name='Дата', **nullable)
    type = models.IntegerField(choices=EVENT_TYPES, verbose_name='Тип')
    result = models.IntegerField(choices=EVENT_RESULT_TYPES, verbose_name='Результат', **nullable)
    courtroom = models.IntegerField(verbose_name='Зал суда', **nullable)
    case = models.ForeignKey('Case', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.get_type_display()}'

    class Meta:
        verbose_name = 'Событие в деле'
        verbose_name_plural = 'События в деле'

class CaseGroup(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    second_inst = models.BooleanField()
    third_inst = models.BooleanField()
    revision = models.BooleanField()

class Advocate(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Адвокат'
        verbose_name_plural = 'Адвокаты'

class CaseDefense(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    defendant = models.ForeignKey('Defendant', verbose_name='Ответчик', on_delete=models.CASCADE)
    advocate = models.ForeignKey('Advocate', verbose_name='Адвокат', on_delete=models.CASCADE, **nullable)
    codex_articles = models.ManyToManyField('codex.CodexArticle', verbose_name='Статьи')
    case = models.ForeignKey('Case', on_delete=models.CASCADE)

    def __str__(self):
        return self.defendant.name

    class Meta:
        verbose_name = 'Ответчик'
        verbose_name_plural = 'Ответчики'

class Defendant(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, db_index=True)
    region = models.IntegerField()
    gender = models.IntegerField(choices=GENDER_TYPES, **nullable)

    def __str__(self):
        return f'{self.name}'