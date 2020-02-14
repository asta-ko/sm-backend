import traceback

import editdistance
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils import timezone

from oi_sud.cases.parsers.result_texts import kp_extractor
from oi_sud.cases.utils import normalize_name, parse_name_and_get_gender
from oi_sud.core.consts import region_choices
from oi_sud.core.utils import nullable, DictDiffer

CASE_TYPES = (
    (1, 'Дело об административном правонарушении'),
    (2, 'Уголовное дело'),
    (3, 'Производство по материалам')
)

CASE_STAGES = (
    (1, 'Первая инстанция'),
    (2, 'Апелляция/первый пересмотр'),
    (3, 'Новое рассмотрение в первой инстанции')
)

GENDER_TYPES = (
    (1, 'Ж'),
    (2, 'М'),
)

PENALTY_TYPES = (
    ('fine', 'Штраф'),
    ('works', 'Обязательные работы'),
    ('arrest', 'Арест'),
    ('term', 'Срок'),
    ('other', 'Другое'),
    ('error', 'Ошибка')

)


class CaseManager(models.Manager):

    def create_case_from_data(self, item):
        with reversion.create_revision():
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
                    CaseEvent.objects.create(**event)
                print('saved case ', case)
                return case
            except Exception:
                print(traceback.format_exc())


class Case(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entry_date = models.DateField(verbose_name='Дата поступления', db_index=True)  # поступление в суд
    result_date = models.DateField(verbose_name='Дата решения', **nullable)  # рассмотрение
    result_published_date = models.DateField(verbose_name='Дата публикации решения', **nullable)  # публикация решения
    result_valid_date = models.DateField(verbose_name='Решение вступило в силу', **nullable)  # решение вступило в силу
    forwarding_to_higher_court_date = models.DateField(verbose_name='Дата направления в вышестоящий суд', **nullable)
    appeal_date = models.DateField(verbose_name='Дата рассмотрения жалобы', **nullable)
    appeal_result = models.CharField(max_length=120, verbose_name='Результат обжалования', **nullable)
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
    codex_articles = models.ManyToManyField('codex.CodexArticle', verbose_name='Статьи', related_name='cases')
    result_type = models.CharField(max_length=200, verbose_name='Решение по делу', **nullable)
    result_text = models.TextField(verbose_name='Текст решения', **nullable)  # Текст решения
    type = models.IntegerField(choices=CASE_TYPES, verbose_name='Тип судопроизводства')  # тип судопроизводства
    stage = models.IntegerField(choices=CASE_STAGES,
                                verbose_name='Инстанция')  # первая инстанция, обжалование, пересмотр, кассация
    url = models.URLField(verbose_name='URL', unique=True, **nullable)
    linked_cases = models.ManyToManyField("self", symmetrical=True, **nullable)

    linked_case_number = ArrayField(models.CharField(max_length=50), verbose_name='Номер связанного дела',
                                    **nullable)  # Москва
    linked_case_url = ArrayField(models.URLField(), verbose_name='Ссылка на связанное дело', **nullable)  # Москва
    text_search = SearchVectorField(null=True)

    objects = CaseManager()

    class Meta:
        verbose_name = 'Дело'
        verbose_name_plural = 'Все дела'
        indexes = [
            GinIndex(fields=['text_search'])
        ]

    def __str__(self):

        articles_list = ','.join([str(x) for x in self.codex_articles.all()])
        return f'{self.case_number} {articles_list} {self.court}'

    def save(self, *args, **kwargs):

        just_created = self.pk is None
        super(Case, self).save(*args, **kwargs)
        if just_created:
            self.process_result_text()

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
        return f'{settings.BASE_URL}/admin/cases/{self.get_codex_type()}case/{self.pk}/change/'

    def get_result_text_url(self):
        return f"{settings.BASE_URL}{reverse('case-result-text', kwargs={'case_id': self.pk})}"

    def get_history_link(self):
        return settings.BASE_URL + reverse(f'admin:cases_{self.get_codex_type()}case_history', args=(self.id,))

    @staticmethod
    def autocomplete_search_fields():
        return 'case_number',

    def update_case(self):

        try:
            codex = None
            parser = None
            if self.type == 1:
                codex = 'koap'
            elif self.type == 2:
                codex = 'uk'
            if self.court.site_type == 1:
                from oi_sud.cases.parsers.rf import FirstParser
                parser = FirstParser(court=self.court, stage=self.stage, codex=codex)
            elif self.court.site_type == 2:
                from oi_sud.cases.parsers.rf import SecondParser
                parser = SecondParser(court=self.court, stage=self.stage, codex=codex)
            elif self.court.site_type == 3:
                from oi_sud.cases.parsers.moscow import MoscowParser
                parser = MoscowParser(stage=self.stage, codex=codex)

            url = self.url
            if self.court.site_type != 3:
                url = url + '&nc=1'
            # print(url)
            raw_data = parser.get_raw_case_information(url)
            fresh_data = {i: j for i, j in parser.serialize_data(raw_data).items() if j is not None}
            fresh_data['case'] = {k: v for k, v in fresh_data['case'].items() if v is not None}
            self.update_if_needed(fresh_data)
        except:
            print('error: ', self.url)
            print(traceback.format_exc())

    def update_if_needed(self, fresh_data):

        old_data = self.serialize()
        # print(old_data, fresh_data)

        if not old_data['case'].get('result_text') and fresh_data['case'].get('result_text'):
            fresh_data['case']['result_published_date'] = timezone.now()
            self.process_result_text()
        if settings.TEST_MODE:  # for tests
            fresh_data['case']['case_number'] = '000'
        with reversion.create_revision():
            diff_keys = []
            if fresh_data['case'] != old_data['case']:
                print(f'Updating case... {self}')
                diff_keys += DictDiffer(fresh_data['case'], old_data['case']).get_all_diff_keys()
                self.__dict__.update(fresh_data['case'])
                self.save()

            if fresh_data['defenses'] != old_data['defenses']:
                print(f'Updating case defendants... {self}')
                for d in fresh_data['defenses']:
                    articles = d['codex_articles']
                    defendant = d['defendant']
                    defense, created = CaseDefense.objects.get_or_create(defendant=defendant, case=self)
                    if len(articles):
                        defense.codex_articles.set(articles)
                diff_keys.append('defenses')

            if fresh_data['events'] != old_data['events']:
                print(f'Updating case events... {self}')
                for event in fresh_data['events']:
                    event['case'] = self
                    obj, created = CaseEvent.objects.update_or_create(**event)
                diff_keys.append('events')

            if len(diff_keys):
                comment_message = 'Изменено: ' + ', '.join(diff_keys)
                reversion.set_comment(comment_message)

    def serialize(self):

        result = {'case': {}, 'defenses': [], 'events': [], 'codex_articles': []}

        for attribute in ['case_number', 'case_uid', 'protocol_number', 'result_text', 'entry_date', 'result_date',
                          'forwarding_to_higher_court_date', 'forwarding_to_lower_court_date', 'appeal_date',
                          'appeal_result', 'result_type', 'type', 'stage', 'url', 'court', 'judge']:
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

    def process_result_text(self):

        if not self.result_text:
            return

        if self.type != 1:  # пока мы не можем обрабатывать уголовки
            return

        if self.penalties.count() > 1:  # верно для административок
            return

        result = kp_extractor.process(self.result_text)
        try:
            if not result.get('could_not_process'):
                for penalty_type in ['fine', 'arrest', 'works']:
                    if result.get(penalty_type):
                        if result[penalty_type].get('num') and int(result[penalty_type].get('num')) > 8000000:
                            CasePenalty.objects.create(type='error', is_hidden=False, case=self, defendant=self.defendants.first())
                        CasePenalty.objects.create(type=penalty_type, case=self, defendant=self.defendants.first(),
                                                   **result[penalty_type])
                        break
            else:
                CasePenalty.objects.create(type='error', case=self, is_hidden=False, defendant=self.defendants.first())
        except Exception as e:
            print('saving error')
            print(e)

        #if not self.result_type:

        #if result.get('returned'):
        #    self.result_type = 'Возвращено'

        if result.get('cancelled'):
            self.result_type = 'Вынесено постановление о прекращении производства по делу об адм. правонарушении'

        elif result.get('forward'):
            self.result_type = 'Направлено по подведомственности'

        if result.get('returned') or result.get('cancelled') or result.get('forward'):
            self.save()

        # TODO: добавить выдворения


class UKCase(Case):
    class Meta:
        proxy = True
        verbose_name = 'Дело (УК)'
        verbose_name_plural = 'Дела (УК)'
        ordering = ['-entry_date', ]

    # def __str__(self):
    #     articles_list = ','.join([str(x) for x in self.codex_articles.all()])
    #     return f'{self.case_number} {articles_list} {self.court}'


class KoapCase(Case):
    class Meta:
        proxy = True
        verbose_name = 'Дело (КОАП)'
        verbose_name_plural = 'Дела (КОАП)'
        ordering = ['-entry_date', ]

    # def __str__(self):
    #
    #     articles_list = ','.join([str(x) for x in self.codex_articles.all()])
    #     return f'{self.case_number} {articles_list} {self.court}'


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
    type = models.CharField(max_length=200, verbose_name='Тип')
    result = models.CharField(max_length=200, verbose_name='Результат', **nullable)
    courtroom = models.IntegerField(verbose_name='Зал суда', **nullable)
    case = models.ForeignKey('Case', on_delete=models.CASCADE, related_name='events')

    def __str__(self):
        return f'{self.type}'

    class Meta:
        verbose_name = 'Событие в деле'
        verbose_name_plural = 'События в деле'
        ordering = ['date', ]


class Advocate(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Адвокат'
        verbose_name_plural = 'Адвокаты'


class CaseDefense(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    defendant = models.ForeignKey('Defendant', verbose_name='Ответчик', related_name='defenses',
                                  on_delete=models.CASCADE)
    advocate = models.ForeignKey('Advocate', verbose_name='Адвокат', on_delete=models.CASCADE, **nullable)
    codex_articles = models.ManyToManyField('codex.CodexArticle', verbose_name='Статьи')
    case = models.ForeignKey('Case', on_delete=models.CASCADE)

    def __str__(self):
        return self.defendant.name_normalized

    class Meta:
        verbose_name = 'Ответчик в деле'
        verbose_name_plural = 'Ответчики в делах'


class DefendantManager(models.Manager):

    @staticmethod
    def create_from_name(name, region):

        names, gender = parse_name_and_get_gender(name)
        normalized_name = normalize_name(name)
        if len(names) and Defendant.objects.filter(region=region, last_name=names[0], first_name=names[1],
                                                   middle_name=names[2]).exists():  # Совпадают регион и ФИО полностью
            return Defendant.objects.filter(region=region, last_name=names[0], first_name=names[1],
                                            middle_name=names[2]).first()
        elif Defendant.objects.filter(name_normalized=normalized_name,
                                      region=region).exists():  # Совпадают регион, фамилия и инициалы
            qs = Defendant.objects.filter(name_normalized=normalized_name, region=region)
            if not len(names):  # не можем проверить, отдаем первое совпадение
                return qs.first()
            else:
                for d in qs:
                    if d.first_name and d.middle_name:
                        e = editdistance.eval(f'{names[1]} {names[2]}', f'{d.first_name} {d.middle_name}')
                        if e <= 3:  # проверяем, что это то же самое имя и отчество и учитываем возможность опечаток
                            return d
                return qs.first()  # если не можем проверить, берем первое попавшееся
        else:

            d_dict = {'region': region,
                      'name_normalized': normalized_name}
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


class CasePenalty(models.Model):
    type = models.CharField(max_length=10, choices=PENALTY_TYPES, **nullable)
    num = models.IntegerField(**nullable)
    is_hidden = models.BooleanField()
    case = models.ForeignKey(Case, related_name='penalties', on_delete=models.CASCADE)
    defendant = models.ForeignKey('Defendant', on_delete=models.CASCADE, **nullable)

    def __str__(self):

        units_dict = {
            'works': 'в часах',
            'fine': 'в рублях',
            'arrest': 'в сутках'
        }

        if self.is_hidden:
            return f'{self.get_type_display()}: информация скрыта'
        else:
            return f'{self.get_type_display()}: {self.num} ({units_dict[self.type]})'

    class Meta:
        verbose_name = 'Наказание'
        verbose_name_plural = 'Наказания'
        unique_together = ('case', 'defendant')

import reversion

reversion.register(KoapCase)
reversion.register(UKCase)
reversion.register(Case)
reversion.register(CaseDefense)
reversion.register(CaseEvent)
