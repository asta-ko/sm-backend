import logging

import reversion
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import IntegrityError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from oi_sud.cases.parsers.result_texts import kp_extractor
from oi_sud.cases.utils import get_gender, normalize_name, get_or_create_from_name
from oi_sud.core.consts import region_choices
from oi_sud.core.utils import DictDiffer, nullable

logger = logging.getLogger(__name__)

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
    ('warning', 'Предупреждение'),
    ('no_data', 'Нет данных'),
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
                    advocates = defense.get('advocates')
                    prosecutors = defense.get('prosecutors')
                    defendant = defense['defendant']
                    defense = CaseDefense.objects.create(defendant=defendant, case=case)
                    if articles:
                        defense.codex_articles.set(articles)
                    if advocates:
                        defense.advocates.set(advocates)
                    if prosecutors:
                        defense.prosecutors.set(prosecutors)
                for event in item['events']:
                    event['case'] = case
                    CaseEvent.objects.create(**event)
                logger.debug(f'Saved new case: {case}')
                return case
            except Exception as e:
                logger.error(f'Failed to save case: {e}')
                logger.debug(item)


class Case(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entry_date = models.DateField(verbose_name='Дата поступления')  # поступление в суд
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
    actual_url_unknown = models.BooleanField(default=False)
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
    linked_cases = models.ManyToManyField("self", symmetrical=True)

    linked_case_number = ArrayField(models.CharField(max_length=50), verbose_name='Номер связанного дела',
                                    **nullable)  # Москва
    linked_case_url = ArrayField(models.URLField(), verbose_name='Ссылка на связанное дело', **nullable)  # Москва
    text_search = SearchVectorField(null=True)

    objects = CaseManager()

    class Meta:

        verbose_name = 'Дело'
        verbose_name_plural = 'Все дела'
        indexes = [
            GinIndex(fields=['text_search']),
            models.Index(fields=['-entry_date', '-result_date', 'result_type', 'appeal_result']),
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

    def get_advocates(self):
        return Advocate.objects.filter(a_defenses__case=self)

    def get_prosecutors(self):
        return Prosecutor.objects.filter(p_defenses__case=self)

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
                # проверяем, на месте ли карточка
                url_is_actual = parser.check_url_actual(url)
                if not url_is_actual:
                    # если нет, пытаемся получить новый урл
                    url = self.search_for_new_url()
                    if not url:
                        print('didnt get New url')

            raw_data = parser.get_raw_case_information(url)
            fresh_data = {i: j for i, j in parser.serialize_data(raw_data).items() if j is not None}
            fresh_data['case'] = {k: v for k, v in fresh_data['case'].items() if v is not None}
            self.update_if_needed(fresh_data)
        except Exception as e:  # NOQA
            #raise
            import traceback
            traceback.print_exc()
            logger.error(f'Failed to update case: {e}, case admin url: {self.get_admin_url()}, case url: {self.url}')

    # ищем новую карточку взамен протухшей. неактуально для Москвы.
    def search_for_new_url(self):
        from oi_sud.cases.parsers.rf import RFCasesGetter
        return RFCasesGetter(self.type).get_moved_case_url(self)

    # если есть изменения, обновляем дело (ничего при этом не удаляя)
    def update_if_needed(self, fresh_data):

        old_data = self.serialize()

        if not old_data['case'].get('result_text') and fresh_data['case'].get('result_text'):
            fresh_data['case']['result_published_date'] = timezone.now()
            self.process_result_text()
        if settings.TEST_MODE:  # for tests
            fresh_data['case']['case_number'] = '000'
        with reversion.create_revision():
            diff_keys = []
            if fresh_data['case'] != old_data['case']:
                logger.debug(f'Updating case... {self}')
                diff_keys += DictDiffer(fresh_data['case'], old_data['case']).get_all_diff_keys()
                self.__dict__.update(fresh_data['case'])
                self.save(update_fields=fresh_data['case'].keys())

            if fresh_data['defenses'] != old_data['defenses']:
                logger.debug(f'Updating case defendants... {self}')
                for d in fresh_data['defenses']:
                    articles = d['codex_articles']
                    defendant = d['defendant']
                    advocates = d.get('advocates')
                    prosecutors = d.get('prosecutors')
                    defense, created = CaseDefense.objects.get_or_create(defendant=defendant, case=self)
                    if len(articles):
                        defense.codex_articles.set(articles)
                    if advocates:
                        defense.advocates.set(advocates)
                    if prosecutors:
                        defense.prosecutors.set(prosecutors)

                diff_keys.append('defenses')

            if fresh_data['events'] != old_data['events']:
                logger.debug(f'Updating case events... {self}')
                for event in fresh_data['events']:
                    event['case'] = self
                    obj, created = CaseEvent.objects.update_or_create(**event)
                diff_keys.append('events')

            if len(diff_keys):
                comment_message = 'Изменено: ' + ', '.join(diff_keys)
                reversion.set_comment(comment_message)

    # приводим дело в формат raw_case_data для сравнения с новыми данными
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
            for attribute in ['defendant', 'advocates', 'prosecutors', 'codex_articles']:
                if getattr(defense, attribute) is not None:
                    d_dict[attribute] = getattr(defense, attribute)

            result['defenses'].append(d_dict)

        result['codex_articles'] = self.codex_articles.all()

        return result

    def process_result_text(self):

        # пока мы не можем обрабатывать уголовки. третье условие верно только для административок
        if not self.result_text or self.type != 1 or  self.penalties.count() > 1:
            return

        result = kp_extractor.process(self.result_text)  # получаем результат

        if result and not result.get('could_not_process') \
                and (result.get('returned') or result.get('cancelled') or result.get('forward')):
            self.add_result_type(result)
            return  # если у нас есть результат, и это возврат, отмена или направление по подведомственности,
            # сохраняем его в результат дела, если он пустой, и останавливаемся.

        try:
            if result.get('could_not_process'):  # если результат с ошибкой, сохраняем 'нет данных'
                CasePenalty.objects.create(type='no_data', case=self, is_hidden=False,
                                           defendant=self.defendants.first())
            else:
                # если результат без ошибки, сохраняем наказание
                for penalty_type in ['fine', 'arrest', 'works']:
                    if result.get(penalty_type):
                        CasePenalty.objects.create(type=penalty_type, case=self, defendant=self.defendants.first(),
                                                   **result[penalty_type])
                        break
        except IntegrityError:
            logger.warning(f'Saving penalty integrity error {self.get_admin_url()}')
        except Exception as e:
            logger.error(f'Saving penalty error {e}: {self.get_admin_url()}')
            CasePenalty.objects.filter(case=self).delete()
            CasePenalty.objects.create(type='error', case=self, is_hidden=False, defendant=self.defendants.first())
            # сохраняем ошибку

        # TODO: добавить выдворения

    def add_result_type(self, result):
        if self.result_type:
            return

        if result.get('returned'):
            self.result_type = 'Возвращено'

        if result.get('cancelled'):
            self.result_type = 'Вынесено постановление о прекращении производства по делу об адм. правонарушении'

        if result.get('forward'):
            self.result_type = 'Направлено по подведомственности'

        if result.get('returned') or result.get('cancelled') or result.get('forward'):
            self.save()


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


class AdvocateManager(models.Manager):
    @staticmethod
    def create_from_name(name, region):
        return get_or_create_from_name(name, region, Advocate, gender_needed=False)


class Advocate(models.Model):
    name_normalized = models.CharField(max_length=50)
    region = models.IntegerField(choices=region_choices, **nullable)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=150, **nullable)
    middle_name = models.CharField(max_length=150, **nullable)
    last_name = models.CharField(max_length=150, **nullable)
    objects = AdvocateManager()

    def __str__(self):
        return f'{self.name_normalized}'

    class Meta:
        verbose_name = 'Адвокат'
        verbose_name_plural = 'Адвокаты'


class ProsecutorManager(models.Manager):
    @staticmethod
    def create_from_name(name, region):
        return get_or_create_from_name(name, region, Prosecutor, gender_needed=False)


class Prosecutor(models.Model):
    name_normalized = models.CharField(max_length=50)
    region = models.IntegerField(choices=region_choices, **nullable)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=150, **nullable)
    middle_name = models.CharField(max_length=150, **nullable)
    last_name = models.CharField(max_length=150, **nullable)
    objects = ProsecutorManager()

    def __str__(self):
        return f'{self.name_normalized}'

    class Meta:
        verbose_name = 'Прокурор'
        verbose_name_plural = 'Прокуроры'


class CaseDefense(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    defendant = models.ForeignKey('Defendant', verbose_name='Ответчик', related_name='defenses',
                                  on_delete=models.CASCADE)
    advocates = models.ManyToManyField('Advocate', verbose_name='Адвокаты', related_name='a_defenses')
    prosecutors = models.ManyToManyField('Prosecutor', verbose_name='Прокуроры', related_name='p_defenses')
    codex_articles = models.ManyToManyField('codex.CodexArticle', verbose_name='Статьи')
    case = models.ForeignKey('Case', on_delete=models.CASCADE, related_name='defenses')

    def __str__(self):
        return self.defendant.name_normalized

    class Meta:
        verbose_name = 'Ответчик в деле'
        verbose_name_plural = 'Ответчики в делах'


class DefendantManager(models.Manager):

    @staticmethod
    def create_from_name(name, region):
        return get_or_create_from_name(name, region, Defendant, gender_needed=True)


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

    def get_gender(self):
        if self.first_name:
            return get_gender(self.first_name, self.last_name)
        else:
            return get_gender(None, self.name_normalized.split(' ')[0])

    class Meta:
        verbose_name = 'Ответчик'
        verbose_name_plural = 'Ответчики'


class CasePenalty(models.Model):
    type = models.CharField(max_length=10, choices=PENALTY_TYPES, db_index=True, **nullable)
    num = models.IntegerField(**nullable)
    is_hidden = models.BooleanField()
    case = models.ForeignKey(Case, related_name='penalties', on_delete=models.CASCADE)
    defendant = models.ForeignKey('Defendant', on_delete=models.CASCADE, **nullable)

    def __str__(self):

        units_dict = {
            'works': 'в часах',
            'fine': 'в рублях',
            'arrest': 'в сутках',
        }

        if self.is_hidden:
            return f'{self.get_type_display()}: информация скрыта'
        elif self.type == 'error':
            return 'Ошибка при получении'
        elif self.type == 'warning':
            return 'Предупреждение'
        elif self.type == 'no_data':
            return 'Нет данных'
        else:
            return f'{self.get_type_display()}: {self.num} ({units_dict[self.type]})'

    class Meta:
        verbose_name = 'Наказание'
        verbose_name_plural = 'Наказания'
        unique_together = ('case', 'defendant')


reversion.register(KoapCase)
reversion.register(UKCase)
reversion.register(Case)
reversion.register(CaseDefense)
reversion.register(CaseEvent)
