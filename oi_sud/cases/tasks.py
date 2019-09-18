from celery import shared_task
from celery_once import QueueOnce
import traceback

from oi_sud.cases.parsers.rf import RFCasesGetter
from oi_sud.cases.grouper import grouper
from oi_sud.core.utils import chunks
from oi_sud.courts.models import Court
from oi_sud.cases.models import Case
from oi_sud.core.consts import region_choices


@shared_task(base=QueueOnce, once={'graceful': True})
def main_get_cases():
    for region in region_choices:
        get_cases_from_region.s(region[0]).apply_async(queue='main')

@shared_task
def get_cases_from_region(region):
    region_courts = Court.objects.filter(region=region)
    chunked_courts = chunks(region_courts.values_list('id', flat=True), 10)

    for chunk in chunked_courts:
        get_koap_cases_first.s(chunk).apply_async(queue='other')
        get_koap_cases_second.s(chunk).apply_async(queue='other')
        get_uk_cases_first.s(chunk).apply_async(queue='other')
        get_uk_cases_second.s(chunk).apply_async(queue='other')
    grouper.group_cases(region=region)


@shared_task
def update_cases(court_id):
    court = Court.objects.get(pk=court_id)
    cases = Case.objects.filter(court = court)
    for case in cases:
        case.update_case()

@shared_task
def get_koap_cases_first(courts):
    RFCasesGetter('koap').get_cases(1, courts)

@shared_task
def get_koap_cases_second(courts):
    RFCasesGetter('koap').get_cases(2, courts)

@shared_task
def get_uk_cases_first(courts):
    RFCasesGetter('uk').get_cases(1, courts)

@shared_task
def get_uk_cases_second(courts):
    RFCasesGetter('uk').get_cases(2, courts)
