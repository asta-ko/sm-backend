import traceback
from dateutil.relativedelta import relativedelta

from dateparser.conf import settings as dateparse_settings
from django.utils.timezone import get_current_timezone

from .consts import EVENT_TYPES, EVENT_RESULT_TYPES, RESULT_TYPES, APPEAL_RESULT_TYPES
from .models import Case
from oi_sud.cases.parsers.rf import FirstParser, SecondParser
from  oi_sud.cases.parsers.moscow import MoscowParser
dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False



class CasesUpdater(object):

    def __init__(self, codex=None):
        self.codex = codex

    def update_cases(self):
        for case in Case.objects.filter(type=self.codex):
            try:
                if case.court.site_type == 1:
                    p = FirstParser(court=case.court, stage=1, type=self.codex)
                elif case.court.site_type == 2:
                    p = SecondParser(court=case.court, stage=1, type=self.codex)
                elif case.court.site_type == 3:
                    p = MoscowParser(stage=1, type=self.codex)
                url = case.url + '&nc=1'
                # print(url)
                raw_data = p.get_raw_case_information(url)
                fresh_data = {i: j for i, j in p.serialize_data(raw_data).items() if j != None}
                case.update_if_needed(fresh_data)
            except:
                print('error: ', case.url)
                print(traceback.format_exc())

    def get_first_cases(self, case):
        params = {'stage': 1, 'defendants__in': case.defendants.all()}
        other_params_list = []

        if case.result_date:
            other_params_list.append({'appeal_date': case.result_date})
        if case.case_uid:
            other_params_list.append({'case_uid': case.case_uid})
        if case.protocol_number:
            other_params_list.append({'protocol_number': case.protocol_number})
            other_params_list.append({'result_text__contains': case.protocol_number})

        for item in other_params_list:
            merged_params = {**params, **item}
            # print(merged_params)
            if Case.objects.filter(**merged_params).exists():
                # print(item)
                return Case.objects.filter(**merged_params)

    def get_second_case(self, case):
        params = {'stage': 2, 'defendants__in': case.defendants.all()}
        other_params_list = []

        if case.appeal_date:
            other_params_list.append({'result_date': case.appeal_date})
        if case.case_uid:
            other_params_list.append({'case_uid': case.case_uid})
        if case.protocol_number:
            other_params_list.append({'protocol_number': case.protocol_number})
            other_params_list.append({'result_text__contains': case.protocol_number})

        other_params_list.append({'result_text__contains': case.case_number})

        for item in other_params_list:
            merged_params = {**params, **item}
            # print(merged_params)
            if Case.objects.filter(**merged_params).exists():
                # print(item)
                return Case.objects.filter(**merged_params)

    def group_cases(self, region):
        first_cases_appealed = Case.objects.filter(court__region=region, appeal_result__isnull=False, linked_cases=None)
        second_cases = Case.objects.filter(stage=2, court__region=region)
        for case in first_cases_appealed:
            second_cases = self.get_second_case(case)
            if second_cases:
                case.linked_cases.add(*second_cases)

        first_cases_not_found = Case.objects.filter(stage=1, court__region=region, appeal_result__isnull=False,
                                                    linked_cases=None)
        second_instance_cases_not_found = Case.objects.filter(stage=2, court__region=region, linked_cases=None)

        # print(len(first_cases_appealed), 'first_cases_appealed')
        print(len(first_cases_not_found), 'first_cases_not_found')
        # print(len(second_cases), 'second_cases_all')
        print(len(second_instance_cases_not_found), 'second_cases_not_found')

        for case in second_instance_cases_not_found:
            first_cases = self.get_first_cases(case)
            if first_cases:
                case.linked_cases.add(*first_cases)
                print('Yikes!')

        first_cases_not_found = Case.objects.filter(stage=1, court__region=region, appeal_result__isnull=False,
                                                    linked_cases=None)
        second_instance_cases_not_found = Case.objects.filter(stage=2, court__region=region, linked_cases=None)
        # print(len(first_cases_appealed), 'first_cases_appealed')
        print(len(first_cases_not_found), 'first_cases_not_found')
        # print(len(second_cases), 'second_cases_all')
        print(len(second_instance_cases_not_found), 'second_cases_not_found')

        for case in first_cases_not_found:
            c = second_instance_cases_not_found.filter(defendants__in=case.defendants.all(),
                                                       entry_date__gte=case.result_date,
                                                       entry_date__lte=case.result_date + relativedelta(months=3))
            if len(c):
                case.linked_cases.add(*c)

        for case in second_instance_cases_not_found:
            c = first_cases_not_found.filter(defendants__in=case.defendants.all(), result_date__lt=case.entry_date,
                                             result_date__year=case.entry_date.year)
            if len(c):
                print([x.case_number for x in c])
                case.linked_cases.add(*c)

        # first_cases_not_found = Case.objects.filter(stage=1, court__region=region, appeal_result__isnull=False,
        #                                             linked_cases=None)
        # second_instance_cases_not_found = Case.objects.filter(stage=2, court__region=region, linked_cases=None)
        #
        # for case in first_cases_not_found:
        #     print(case.defendants.all())
        #
        # for case in second_instance_cases_not_found:
        #     print(case.defendants.all())
