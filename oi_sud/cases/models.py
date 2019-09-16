import editdistance
import traceback
from django.db import models
from django.urls import reverse

from oi_sud.cases.consts import RESULT_TYPES, EVENT_TYPES, EVENT_RESULT_TYPES, APPEAL_RESULT_TYPES
from oi_sud.core.utils import nullable
from oi_sud.cases.utils import normalize_name, parse_name_and_get_gender
from oi_sud.core.consts import region_choices




CASE_TYPES = (
    (1, 'Дело об административном правонарушении'),
    (2, 'Уголовное дело'),
    (3, 'Производство по материалам')
)

CASE_STAGES = (
    (1, 'Первая инстанция'),
    (2, 'Аппеляция/первый пересмотр'),
    (3, 'Новое рассмотрение в первой инстанции')
)

GENDER_TYPES = (
    (1, 'Ж'),
    (2, 'М'),
)


class CaseManager(models.Manager):

    def create_case_from_data(self, item):
        try:
            case = Case.objects.create(**item['case'])
            case.codex_articles.set(item['codex_articles'])
            for defense in item['defenses']:
                articles = defense['codex_articles']
                defendant = defense['defendant']
                defense = CaseDefense.objects.create(defendant=defendant, case=case)
                if len(articles):
                    defense.codex_articles.set(articles)
            for event in item['events']:
                event['case'] = case
                case_event = CaseEvent.objects.create(**event)
            print('saved case ', case)
        except Exception as e:
            print(traceback.format_exc())


class Case(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entry_date = models.DateField(verbose_name='Дата поступления', db_index=True)  # поступление в суд
    result_date = models.DateField(verbose_name='Дата решения', **nullable)  # рассмотрение
    result_published = models.DateField(verbose_name='Дата публикации решения', **nullable)  # публикация решения
    result_valid = models.DateField(verbose_name='Решение вступило в силу', **nullable)  # решение вступило в силу
    forwarding_to_higher_court_date = models.DateField(verbose_name='Дата направления в вышестоящий суд', **nullable)
    appeal_date = models.DateField(verbose_name='Дата рассмотрения жалобы', **nullable)
    appeal_result = models.IntegerField(verbose_name='Результат обжалования', choices=APPEAL_RESULT_TYPES, **nullable)
    forwarding_to_lower_court_date = models.DateField(verbose_name='Дата направления в нижестоящий суд', **nullable)
    judge = models.ForeignKey('courts.Judge', verbose_name='Судья', on_delete=models.CASCADE, **nullable)
    court = models.ForeignKey('courts.Court', verbose_name='Cуд', on_delete=models.CASCADE)
    defendants = models.ManyToManyField('Defendant', through='CaseDefense', related_name='cases')
    defendants_hidden = models.BooleanField(default=False)
    advocates = models.ManyToManyField('Advocate', through='CaseDefense')
    case_number = models.CharField(max_length=50, verbose_name='Номер дела')  # Номер дела
    case_uid = models.CharField(max_length=50, verbose_name='ID в sudrf', **nullable)  # Уникальный id в системе sudrf
    protocol_number = models.CharField(max_length=50, verbose_name='Номер протокола',
                                       **nullable)  # номер протокола (для дел об АП)
    codex_articles = models.ManyToManyField('codex.CodexArticle', verbose_name='Статьи')
    result_type = models.IntegerField(choices=RESULT_TYPES, verbose_name='Решение по делу', **nullable)
    result_text = models.TextField(verbose_name='Текст решения', **nullable)  # Текст решения
    type = models.IntegerField(choices=CASE_TYPES, verbose_name='Тип судопроизводства')  # тип судопроизводства
    stage = models.IntegerField(choices=CASE_STAGES,
                                verbose_name='Инстанция')  # первая инстанция, обжалование, пересмотр, кассация
    #group = models.ForeignKey('CaseGroup', on_delete=models.CASCADE, related_name='group_cases',**nullable)  # ссылки на аппеляции и пересмотры
    url = models.URLField(verbose_name='URL', unique=True, **nullable)
    linked_cases = models.ManyToManyField("self", symmetrical=True)
    objects = CaseManager()

    class Meta:
        verbose_name = 'Дело'
        verbose_name_plural = 'Все дела'

    def __str__(self):

        articles_list = ','.join([str(x) for x in self.codex_articles.all()])
        return f'{self.case_number} {articles_list} {self.court}'

    def get_codex_type(self):
        if self.type == 1:
            return 'koap'
        elif self.type == 2:
            return 'uk'

    def get_2_instance_case(self):
        return self.linked_cases.filter(stage=2).first()

    def get_1_instance_case(self):
        return self.linked_cases.filter(stage=1).first()

    def get_admin_url(self):
        return f'/admin/cases/{self.get_codex_type()}case/{self.pk}/change/'

    @staticmethod
    def autocomplete_search_fields():
        return 'case_number',

    def update_if_needed(self, fresh_data):

        old_data = self.serialize()
        #print(old_data, fresh_data)
        if fresh_data['case'] != old_data['case']:
            print(f'Updating case... {self}')
            Case.objects.filter(pk=self.id).update(**fresh_data['case'])

        if fresh_data['defenses'] != old_data['defenses']:
            print(f'Updating case defendants... {self}')
            for d in fresh_data['defenses']:
                articles = d['codex_articles']
                defendant = d['defendant']
                defense, created = CaseDefense.objects.get_or_create(defendant=defendant, case=self)
                if len(articles):
                    defense.codex_articles.set(articles)

        if fresh_data['events'] != old_data['events']:
            print(f'Updating case events... {self}')
            for event in fresh_data['events']:
                event['case'] = self
                obj, created = CaseEvent.objects.update_or_create(**event)

    def serialize(self):

        result = {'case': {}, 'defenses': [], 'events': [], 'codex_articles': []}

        for attribute in ['case_number', 'case_uid', 'protocol_number', 'result_text', 'entry_date', 'result_date',
                          'forwarding_to_higher_court_date', 'forwarding_to_lower_court_date', 'appeal_date',
                          'appeal_result','result_type', 'type', 'stage', 'url', 'court', 'judge']:
            if getattr(self, attribute):
                result['case'][attribute] = getattr(self, attribute)

        for event in CaseEvent.objects.filter(case=self):
            e_dict = {}
            for attribute in ['date', 'type', 'result', 'courtroom']:
                if getattr(event, attribute) is not None:
                    e_dict[attribute] = getattr(event, attribute)
            result['events'].append(e_dict)

        for defense in CaseDefense.objects.filter(case=self):
            d_dict = {}
            for attribute in ['defendant', 'advocate']:
                if getattr(defense, attribute) is not None:
                    d_dict[attribute] = getattr(defense, attribute)

            d_dict['codex_articles'] = []

            for a in defense.codex_articles.all():
                d_dict['codex_articles'].append(a)

            result['defenses'].append(d_dict)

        result['codex_articles'] = self.codex_articles.all()

        return result


class UKCase(Case):
    class Meta:
        proxy = True
        verbose_name = 'Дело (УК)'
        verbose_name_plural = 'Дела (УК)'


class KoapCase(Case):
    class Meta:
        proxy = True
        verbose_name = 'Дело (КОАП)'
        verbose_name_plural = 'Дела (КОАП)'


class LinkedCasesProxy(Case.linked_cases.through):
    class Meta:
        proxy = True

    def get_pk(self):
        return self.to_case.pk

    def get_codex_type(self):
        return self.to_case.get_codex_type()

    def __str__(self):
        return str(self.to_case)

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


class Advocate(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Адвокат'
        verbose_name_plural = 'Адвокаты'


class CaseDefense(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    defendant = models.ForeignKey('Defendant', verbose_name='Ответчик', related_name='defenses', on_delete=models.CASCADE)
    advocate = models.ForeignKey('Advocate', verbose_name='Адвокат', on_delete=models.CASCADE, **nullable)
    codex_articles = models.ManyToManyField('codex.CodexArticle', verbose_name='Статьи')
    case = models.ForeignKey('Case', on_delete=models.CASCADE)

    def __str__(self):
        return self.defendant.name_normalized

    class Meta:
        verbose_name = 'Ответчик в деле'
        verbose_name_plural = 'Ответчики в делах'

class DefendantManager(models.Manager):
    def create_from_name(self, name, region):

        names, gender = parse_name_and_get_gender(name)
        normalized_name = normalize_name(name)
        if len(names) and Defendant.objects.filter(region=region, last_name=names[0], first_name=names[1], middle_name=names[2]).exists(): #Совпадают регион и ФИО полностью
                return Defendant.objects.filter(region=region, last_name=names[0], first_name=names[1], middle_name=names[2]).first()
        elif Defendant.objects.filter(name_normalized=normalized_name, region=region).exists(): #Совпадают регион, фамилия и инициалы
            qs = Defendant.objects.filter(name_normalized=normalized_name, region=region)
            if not len(names): #не можем проверить, отдаем первое совпадение
                return qs.first()
            else:
                for d in qs:
                    if d.first_name and d.middle_name:
                        e = editdistance.eval(f'{names[1]} {names[2]}', f'{d.first_name} {d.middle_name}')
                        if e <= 3: #проверяем, что это то же самое имя и отчество и учитываем возможность опечаток
                            return d
                return qs.first() #если не можем проверить, берем первое попавшееся
        else:

            d_dict = {'region':region,
                      'name_normalized':normalized_name}
            if len(names):
                d_dict['last_name'] = names[0]
                d_dict['first_name'] = names[1]
                d_dict['middle_name'] = names[2]
            if gender:
                d_dict['gender'] = gender
            defendant = Defendant(**d_dict)
            defendant.save()
            return defendant

class Defendant(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    region = models.IntegerField(choices=region_choices)
    gender = models.IntegerField(choices=GENDER_TYPES, **nullable)
    name_normalized = models.CharField(max_length=150, db_index=True, **nullable)
    first_name = models.CharField(max_length=150, **nullable)
    middle_name = models.CharField(max_length=150, **nullable)
    last_name = models.CharField(max_length=150, **nullable)
    objects = DefendantManager()

    @staticmethod
    def autocomplete_search_fields():
        return 'name_normalized',

    def __str__(self):
        return f'{self.name_normalized}'

    def normalize_name(self):
        return normalize_name(self.name)

    class Meta:
        verbose_name = 'Ответчик'
        verbose_name_plural = 'Ответчики'
