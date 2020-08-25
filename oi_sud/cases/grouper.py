import logging

from dateparser.conf import settings as dateparse_settings
from dateutil.relativedelta import relativedelta
from django.utils.timezone import get_current_timezone

from .models import Case

logger = logging.getLogger(__name__)

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False


class CasesGrouper(object):
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
            if Case.objects.filter(**merged_params).exists():
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
            if Case.objects.filter(**merged_params).exists():
                return Case.objects.filter(**merged_params)

    def group_moscow_cases(self):

        cases_appealed_by_casenum = Case.objects.filter(linked_case_number__isnull=False)
        for case in cases_appealed_by_casenum:
            casenums = case.linked_case_number
            found_cases = Case.objects.filter(case_number__in=casenums)
            case.linked_cases.add(*found_cases)
        # first_cases_not_found = Case.objects.filter(stage=1, appeal_result__isnull=False,
        #                                             linked_cases=None)
        second_instance_cases_not_found = Case.objects.filter(stage=2, linked_cases=None)
        for case in second_instance_cases_not_found:
            first_cases = self.get_first_cases(case)
            if first_cases:
                case.linked_cases.add(*first_cases)

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

        for case in second_instance_cases_not_found:
            first_cases = self.get_first_cases(case)
            if first_cases:
                case.linked_cases.add(*first_cases)

        first_cases_not_found = Case.objects.filter(stage=1, court__region=region, appeal_result__isnull=False,
                                                    linked_cases=None)
        second_instance_cases_not_found = Case.objects.filter(stage=2, court__region=region, linked_cases=None)
        # logger.debug(f'{len(first_cases_appealed)} first_cases_appealed')
        # logger.debug(f'{len(first_cases_not_found)} first_cases_not_found')
        # logger.debug(f'{len(second_cases)} second_cases_all')
        # logger.debug(f'{len(second_instance_cases_not_found)} second_cases_not_found')

        for case in first_cases_not_found:

            if case.result_date:
                c = second_instance_cases_not_found.filter(defendants__in=case.defendants.all(),
                                                           entry_date__gte=case.result_date,
                                                           entry_date__lte=case.result_date + relativedelta(months=3))
                if len(c):
                    case.linked_cases.add(*c)

        for case in second_instance_cases_not_found:
            c = first_cases_not_found.filter(defendants__in=case.defendants.all(), result_date__lt=case.entry_date,
                                             result_date__year=case.entry_date.year)
            if len(c):
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


grouper = CasesGrouper()
