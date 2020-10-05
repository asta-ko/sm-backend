import copy
import logging
from datetime import timedelta

import reversion
from django.utils import timezone
from oi_sud.cases.models import Case, CaseEvent, CaseDefense
from oi_sud.core.utils import DictDiffer, get_query_key

logger = logging.getLogger(__name__)


class MergerUpdater:

    def merge_duplicates(self, filters):

        merges_count = 0
        while True:
            if Case.objects.filter(**filters).count() > 1:
                duplicates = Case.objects.filter(**filters)
                merges_count += 1
                case1, case2 = duplicates[0], duplicates[1]
                new_data = case2.serialize()
                case2.delete()
                self.update_if_needed(case1, new_data)

            else:
                break

    def update_case(self, case):

        from oi_sud.cases.parsers.rf import FirstParser, SecondParser
        from oi_sud.cases.parsers.moscow import MoscowParser

        try:
            parser = None
            codex = 'koap' if case.type == 1 else 'uk'
            if case.court.site_type == 1:
                parser = FirstParser(court=case.court, stage=case.stage, codex=codex)
            elif case.court.site_type == 2:
                parser = SecondParser(court=case.court, stage=case.stage, codex=codex)
            elif case.court.site_type == 3:
                parser = MoscowParser(stage=case.stage, codex=codex)

            url = case.url

            if case.court.site_type != 3 and not parser.check_url_actual(url + '&nc=1'):
                # проверяем, на месте ли карточка (для москвы неактуально)
                # если нет, пытаемся получить новый урл
                url = case.search_for_new_url()
                query_case_id = get_query_key(url, 'case_id')
                if url and Case.objects.filter(court=case.court, url__contains=f'case_id={query_case_id}').exists():
                    # получили новый урл и проверяем, не было ли сохранено это дело в базу под этим новым урлом
                    existing_case = Case.objects.filter(court=case.court,
                                                        url__contains=f'case_id={query_case_id}').first()
                    existing_data = existing_case.serialize()
                    existing_data['defenses'] = []
                    existing_data['events'] = []
                    existing_case.delete()

                    if existing_data and not self.cases_data_identical(existing_data, case.serialize()):
                        # дело под новым урлом было сохранено позже, чем текущее дело.
                        # поэтому обновляем текущее имеющимися данными
                        # пока не будем изменять урл, чтобы не было проблем с уникальностью
                        existing_data['case']['url'] = case.url
                        self.update_if_needed(case, existing_data)

            # получаем свежие данные
            raw_data = parser.get_raw_case_information(url)

            # немножко форматируем
            fresh_data = {i: j for i, j in parser.serialize_data(raw_data).items() if j is not None}
            fresh_data['case'] = {k: v for k, v in fresh_data['case'].items() if v is not None}

            # обновляем текущее дело новыми данными
            self.update_if_needed(case, fresh_data)


        except Exception as e:  # NOQA
            # raise
            import traceback
            traceback.print_exc()
            logger.error(f'Failed to update case: {e}, case admin url: {case.get_admin_url()}, case url: {case.url}')

    def process_duplicates(self, case):
        defendants_names = [x.name_normalized for x in case.defendants.all()]
        r_string = rf'({"|".join(defendants_names)})'

        filter_dict = {'stage': case.stage, 'defendants__name_normalized__regex': r_string, 'court': case.court}
        if hasattr(self, 'entry_date'):
            filter_dict['entry_date__gte'] = self.entry_date - timedelta(days=1)
            filter_dict['entry_date__lte'] = self.entry_date + timedelta(days=1)
        if hasattr(self, 'judge'):
            filter_dict['judge'] = self.judge
        if hasattr(self, 'case_number'):
            filter_dict['case_number'] = self.case_number

        self.merge_duplicates(filters=filter_dict)

    @staticmethod
    def cases_data_identical(first_case_data, second_case_data, compare_urls=False):

        f = copy.deepcopy(first_case_data)
        s = copy.deepcopy(second_case_data)

        if not compare_urls:
            if f['case'].get('url'):
                del f['case']['url']
            if s['case'].get('url'):
                del s['case']['url']

        return f == s

    # если есть изменения, обновляем дело (ничего при этом не удаляя)

    def update_if_needed(self, case, fresh_data):

        old_data = case.serialize()

        identical = self.cases_data_identical(old_data, fresh_data)

        # сравниваем два набора данных

        fresh_url = fresh_data['case']['url'].replace('&nc=1', '')
        old_url = old_data['case']['url'].replace('&nc=1', '')

        if fresh_url != old_url and identical:
            # дело было перемещено, ничего не обновилось, изменяем только урл

            case.url = fresh_url
            case.save(update_fields=['url'])

        elif identical:

            # вообще ничего не обновилось
            return

        if not old_data['case'].get('result_text') and fresh_data['case'].get('result_text'):
            # если появился текст
            fresh_data['case']['result_published_date'] = timezone.now()
            case.process_result_text()

        with reversion.create_revision():  # записываем данные об изменениях
            diff_keys = []

            if fresh_data['case'] != old_data['case']:
                # дело обновилось

                logger.debug(f'Updating case... {case}')

                diff_keys += DictDiffer(fresh_data['case'], old_data['case']).get_all_diff_keys()

                case.__dict__.update(fresh_data['case'])

                case.updated_at = timezone.now()
                fields = list(fresh_data['case'].keys()) + ['updated_at', ]
                case.save(update_fields=fields)

            if fresh_data['defenses'] != old_data['defenses']:
                case.defenses.all().delete()
                logger.debug(f'Updating case defenses... {case}')

                for d in fresh_data['defenses']:
                    articles = d['codex_articles']
                    defendant = d['defendant']
                    advocates = d.get('advocates')
                    prosecutors = d.get('prosecutors')
                    defense, created = CaseDefense.objects.get_or_create(defendant=defendant, case=case)
                    if len(articles):
                        defense.codex_articles.set(articles)
                    if advocates:
                        defense.advocates.set(advocates)
                    if prosecutors:
                        defense.prosecutors.set(prosecutors)
                advocate_names = [x.name_normalized for x in case.get_advocates()]
                prosecutors_names = [x.name_normalized for x in case.get_prosecutors()]
                non_defendants_names = advocate_names + prosecutors_names
                if non_defendants_names:
                    for defense in case.defenses.all():
                        if defense.defendant.name_normalized in non_defendants_names:
                            defense.delete()
                diff_keys.append('defenses')

            if fresh_data['events'] != old_data['events']:
                logger.debug(f'Updating case events... {case}')
                case.events.all().delete()
                for event in fresh_data['events']:
                    event['case'] = case
                    CaseEvent.objects.update_or_create(**event)
                diff_keys.append('events')

            fresh_linked_cases_ids = fresh_data.get('linked_cases_ids')

            if fresh_linked_cases_ids and fresh_linked_cases_ids != old_data.get('linked_cases_ids'):
                for case_id in fresh_linked_cases_ids:
                    linked_case = Case.objects.filter(id=case_id).first()
                    if linked_case:
                        case.linked_cases.add(linked_case)
                diff_keys.append('linked_cases')

            if fresh_data['case'].get('linked_case_number'):
                for case_num in fresh_data['case']['linked_case_number']:
                    if not case.linked_cases.filter(case_number=case_num).count():
                        linked_case = Case.objects.filter(case_number=case_num,
                                                          court=fresh_data['case']['court']).first()
                        if linked_case:
                            case.linked_cases.add(linked_case)

            if len(diff_keys):
                comment_message = 'Изменено: ' + ', '.join(diff_keys)
                reversion.set_comment(comment_message)


merger_updater = MergerUpdater()
