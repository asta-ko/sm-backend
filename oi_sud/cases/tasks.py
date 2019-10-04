from celery import chord
from celery import shared_task
from celery.result import allow_join_result
from datetime import timedelta, datetime
from oi_sud.cases.grouper import grouper
from oi_sud.cases.models import Case
from oi_sud.cases.parsers.rf import RFCasesGetter
from oi_sud.core.consts import region_choices
from oi_sud.core.utils import chunks
from oi_sud.courts.models import Court



def get_start_date(delta_days):
    dt = datetime.now() - timedelta(days=delta_days)
    return dt.strftime('%d.%m.%Y')

@shared_task  # (base=QueueOnce, once={'graceful': True})
def main_get_cases(newest=False):
    for region in region_choices:
        get_cases_from_region.s(region=region[0], newest=False).apply_async(queue='main')


@shared_task(bind=True)
def get_cases_from_region(self, region=78, newest=False):
    # progress_recorder = ProgressRecorder(self)
    callback = group_by_region.si(region=region).set(queue="other")
    header = []

    region_courts = Court.objects.filter(region=region)
    chunked_courts = chunks(region_courts.values_list('id', flat=True), 10)

    for chunk in chunked_courts:
        header += [get_koap_cases_first.si(chunk, newest=newest).set(queue="other"),
                   get_koap_cases_second.si(chunk, newest=newest).set(queue="other"),
                   get_uk_cases_first.si(chunk, newest=newest).set(queue="other"),
                   get_uk_cases_second.si(chunk, newest=newest).set(queue="other")
                   ]

    # result_progress, result = progress_chord(header)(callback)
    # result.apply_async()
    result = chord(header)(callback)
    result_count = 0
    with allow_join_result():
        result.get()


@shared_task
def group_by_region(region=None):
    if region:
        grouper.group_cases(region=region)
    return True


@shared_task
def update_cases_by_court(court_id, newest=False, delta_days=3*30):
    court = Court.objects.get(pk=court_id)
    cases = Case.objects.filter(court=court)
    if newest:
        dt = datetime.now() - timedelta(days=delta_days)
        cases = cases.filter(entry_date__gte=dt)
    for case in cases:
        case.update_case()

@shared_task
def update_cases_by_region(region, newest=False, delta_days=3*30):
    cases = Case.objects.filter(court__region=region)
    if newest:
        dt = datetime.now() - timedelta(days=delta_days)
        cases = cases.filter(entry_date__gte=dt)

    for case in cases:
        case.update_case()




@shared_task
def get_koap_cases_first(courts, newest=False):
    entry_date = get_start_date(30*6) if newest else None
    return RFCasesGetter('koap').get_cases(1, courts, entry_date_from=entry_date)

@shared_task
def get_koap_cases_second(courts, newest=False):
    entry_date = get_start_date(30*6) if newest else None
    return RFCasesGetter('koap').get_cases(2, courts, entry_date_from=entry_date)

@shared_task
def get_uk_cases_first(courts, newest=False):
    entry_date = get_start_date(30*6) if newest else None
    return RFCasesGetter('uk').get_cases(1, courts, entry_date_from=entry_date)

@shared_task
def get_uk_cases_second(courts, newest=False):
    entry_date = get_start_date(30*6) if newest else None
    return RFCasesGetter('uk').get_cases(2, courts, entry_date_from=entry_date)

