from django.db import models

from oi_sud.core.utils import nullable

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

EVENT_TYPES = ()

RESULT_TYPES = ()


class Case(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entry_date = models.DateTimeField()  # поступление в суд
    result_date = models.DateTimeField(**nullable)  # рассмотрение
    result_published = models.DateTimeField(**nullable)  # публикация решения
    result_valid = models.DateTimeField(**nullable)  # решение вступило в силу
    judge = models.ForeignKey('courts.Judge', on_delete=models.CASCADE)
    court = models.ForeignKey('courts.Court', on_delete=models.CASCADE)
    defendants = models.ManyToManyField('Defendant')
    case_id = models.CharField(max_length=20, unique=True)  # Номер дела
    system_id = models.CharField(max_length=20, unique=True)  # Уникальный id в системе sudrf
    protocol_number = models.CharField(max_length=20, unique=True, **nullable)  # номер протокола (для дел об АП)
    codex_articles = models.ManyToManyField('codex.CodexArticle')
    result_text = models.TextField(**nullable)  # Текст решения
    # events = models.ManyToManyField('CaseEvent')  # Движение дела
    case_type = models.IntegerField(choices=CASE_TYPES)  # тип судопроизводства
    case_stage = models.IntegerField(choices=CASE_STAGES)  # первая инстанция, обжалование, пересмотр, кассация
    case_group = models.ForeignKey('CaseGroup', on_delete=models.CASCADE)  # ссылки на аппеляции и пересмотры


class CaseEvent(models.Model):
    created_at = models.DateTimeField()
    date = models.DateTimeField()
    type = models.IntegerField(choices=EVENT_TYPES)
    result = models.IntegerField(choices=RESULT_TYPES)
    courtroom = models.IntegerField()
    case = models.ForeignKey('Case', on_delete=models.CASCADE)


class CaseGroup(models.Model):
    second_inst = models.BooleanField()
    third_inst = models.BooleanField()
    revision = models.BooleanField()


class Defendant(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    region = models.IntegerField()
