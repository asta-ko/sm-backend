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

EVENT_TYPES = (
(0,'Передача дела судье'),
(1,'Подготовка дела к рассмотрению'),
(2,'Рассмотрение дела по существу'),
(3,'Обращено к исполнению'),
(4,'Вступление постановления (определения) в законную силу'),
(5,'Направленная копия постановления (определения) ВРУЧЕНА'),
(6,'Вручение копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'),
(7,'Материалы дела сданы в отдел судебного делопроизводства'),
(8,'Направление копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'),
(9,'Протокол (материалы дела) НЕ БЫЛИ возвращены в ТРЕХДНЕВНЫЙ срок'),
(10,'Направленная копия постановления (определения) ВЕРНУЛАСЬ с отметкой о НЕВОЗМОЖНОСТИ ВРУЧЕНИЯ (п. 29.1 Пост. Пленума ВС от 19.12.2013 № 40)'),
(11,'Производство по делу возобновлено'),
(12,'Регистрация поступившего в суд дела'),
(13,'Передача материалов дела судье'),
(14,'Дело сдано в отдел судебного делопроизводства'),
(15,'Провозглашение приговора'),
(16,'Предварительное слушание'),
(17,'Решение в отношении поступившего уголовного дела'),
(18,'Судебное заседание'),
(19,'Сдача материалов дела в архив'),
(20,'Изготовлено постановление о назначении административного наказания в полном объеме'),
(21,'Изготовлено постановление о прекращении в полном объеме'),

)

RESULT_TYPES = (
(0,'Назначено предварительное слушание'),
(1,'Назначено судебное заседание'),
(2,'Рассмотрение отложено'),
(3,'Заседание отложено'),
(4,'Протокол об административном правонарушении (материалы дела) возвращен(ы)  (в пор. ст.29.4 п.4)'),
(5,'Дело возвращено прокурору'),
(6,'Возвращено без рассмотрения'),
(7,'Производство по делу прекращено'),
(8,'Производство по делу приостановлено'),
(9,'Производство прекращено'),
(10,'Вынесено постановление о назначении административного наказания'),
(11,'Вынесено постановление в порядке гл. 51 УПК (о применении ПМ медицинского характера)'),
(12,'Постановление приговора'),
(13,'Провозглашение приговора окончено'),
(14,'Оглашение резолютивной части постановления о назначении административного наказания (изготовление постановления в полном объеме отложено)'),
(15,'Передано по подведомственности'),
(16,'Оглашение резолютивной части постановления о прекращении производства (изготовление постановления в полном объеме отложено)'),
)

GENDER_TYPES = ()


class Case(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entry_date = models.DateTimeField()  # поступление в суд
    result_date = models.DateTimeField(**nullable)  # рассмотрение
    result_published = models.DateTimeField(**nullable)  # публикация решения
    result_valid = models.DateTimeField(**nullable)  # решение вступило в силу
    judge = models.ForeignKey('courts.Judge', on_delete=models.CASCADE, **nullable)
    court = models.ForeignKey('courts.Court', on_delete=models.CASCADE)
    defendants = models.ManyToManyField('Defendant', through='CaseDefense')
    advocates = models.ManyToManyField('Advocate', through='CaseDefense')
    case_number = models.CharField(max_length=50)  # Номер дела
    case_uid = models.CharField(max_length=50, **nullable)  # Уникальный id в системе sudrf
    protocol_number = models.CharField(max_length=50, **nullable)  # номер протокола (для дел об АП)
    codex_articles = models.ManyToManyField('codex.CodexArticle')
    result_text = models.TextField(**nullable)  # Текст решения
    type = models.IntegerField(choices=CASE_TYPES)  # тип судопроизводства
    stage = models.IntegerField(choices=CASE_STAGES)  # первая инстанция, обжалование, пересмотр, кассация
    group = models.ForeignKey('CaseGroup', on_delete=models.CASCADE, **nullable)  # ссылки на аппеляции и пересмотры
    url = models.URLField(**nullable)

    def __str__(self):
        return f'{self.case_uid} {[str(x) for x in self.codex_articles.all()]}'

class CaseEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField()
    type = models.IntegerField(choices=EVENT_TYPES)
    result = models.IntegerField(choices=RESULT_TYPES, **nullable)
    courtroom = models.IntegerField(**nullable)
    case = models.ForeignKey('Case', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.case}: {self.type} {self.date}'

class CaseGroup(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    second_inst = models.BooleanField()
    third_inst = models.BooleanField()
    revision = models.BooleanField()

class Advocate(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class CaseDefense(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    defendant = models.ForeignKey('Defendant', on_delete=models.CASCADE)
    advocate = models.ForeignKey('Advocate', on_delete=models.CASCADE, **nullable)
    codex_articles = models.ManyToManyField('codex.CodexArticle')
    case = models.ForeignKey('Case', on_delete=models.CASCADE)

class Defendant(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    region = models.IntegerField()
    gender = models.IntegerField(choices=GENDER_TYPES, **nullable)

    def __str__(self):
        return f'{self.name}'