from datetime import datetime, timedelta

from celery import chord
from celery import shared_task
from celery.result import allow_join_result
from celery.signals import worker_init
from oi_sud.cases.grouper import grouper
from oi_sud.cases.models import Case
from oi_sud.cases.parsers.moscow import MoscowCasesGetter
from oi_sud.cases.parsers.rf import RFCasesGetter
from oi_sud.core.consts import region_choices
from oi_sud.core.utils import chunks
from oi_sud.courts.models import Court

weekday_regions = [  # Except SPb and Moscow
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    [14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27],
    [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
    [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53],
    [54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66],
    [67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79],
    [82, 83, 86, 87, 89, 92, 94, 95]
]


@worker_init.connect
def limit_chord_unlock_tasks(worker, **kwargs):
    """
    Set max_retries for chord.unlock tasks to avoid infinitely looping
    tasks. (see celery/celery#1700 or celery/celery#2725)
    """
    task = worker.app.tasks['celery.chord_unlock']
    if task.max_retries is None:
        task.max_retries = 15


def get_start_date(delta_days):
    dt = datetime.now() - timedelta(days=delta_days)
    return dt.strftime('%d.%m.%Y')


@shared_task  # (base=QueueOnce, once={'graceful': True})
def main_get_cases(newest=False, codex=None, custom_regions=None):
    if not custom_regions:
        for region in region_choices:
            get_cases_from_region.s(region=region[0], newest=newest, codex=codex).apply_async(queue='main')
    else:
        for region in custom_regions:
            get_cases_from_region.s(region=region, newest=newest, codex=codex).apply_async(queue='main')


@shared_task
def get_cases_by_week_day():
    today_week_day = datetime.today().weekday()
    regions = weekday_regions[today_week_day]

    for region in regions:
        get_cases_from_region.s(region=region, newest=True).apply_async(queue='main')


@shared_task
def update_cases_by_week_day():
    today_week_day = datetime.today().weekday()
    regions = weekday_regions[today_week_day]

    for region in regions:
        update_cases_by_region.s(region, newest=True).apply_async(queue='other')


@shared_task
def update_all_cases():
    for region in region_choices:
        region_courts = Court.objects.exclude(type=9).filter(region=region[0]).values_list('id', flat=True)
        for court in region_courts:
            update_cases_by_court.s(court, newest=False).apply_async(queue='other')


@shared_task  # (bind=True)
def get_cases_from_region(region=78, newest=False, codex=None):
    # progress_recorder = ProgressRecorder(self)
    callback = group_by_region.si(region=region).set(queue="grouper")
    header = []

    region_courts = Court.objects.exclude(type=9).filter(region=region)
    chunked_courts = chunks(region_courts.values_list('id', flat=True), 2)

    for chunk in chunked_courts:

        if not codex:
            header += [get_koap_cases_first.si(chunk, newest=newest).set(queue="other"),
                       get_koap_cases_second.si(chunk, newest=newest).set(queue="other"),
                       get_uk_cases_first.si(chunk, newest=newest).set(queue="other"),
                       get_uk_cases_second.si(chunk, newest=newest).set(queue="other")]
        elif codex == 'koap':
            header += [get_koap_cases_first.si(chunk, newest=newest).set(queue="other"),
                       get_koap_cases_second.si(chunk, newest=newest).set(queue="other")]
        elif codex == 'uk':
            header += [get_uk_cases_first.si(chunk, newest=newest).set(queue="other"),
                       get_uk_cases_second.si(chunk, newest=newest).set(queue="other")]

    # result_progress, result = progress_chord(header)(callback)
    # result.apply_async()
    result = chord(header)(callback)
    with allow_join_result():
        result.get()


@shared_task
def group_by_region(region=None):
    if region:
        grouper.group_cases(region=region)
    return True


@shared_task
def group_moscow_cases():
    grouper.group_moscow_cases()
    return True


@shared_task
def update_cases_by_court(court_id, newest=False, delta_days=3 * 30):
    court = Court.objects.get(pk=court_id)
    too_fresh_date = datetime.now() - timedelta(hours=8)
    cases = Case.objects.filter(court=court, updated_at__lte=too_fresh_date)
    if newest:
        dt = datetime.now() - timedelta(days=delta_days)
        cases = cases.filter(entry_date__gte=dt)
    for case in cases:
        case.update_case()


@shared_task
def update_cases_by_region(region, newest=False, delta_days=3 * 30):
    cases = Case.objects.filter(court__region=region)
    if newest:
        dt = datetime.now() - timedelta(days=delta_days)
        cases = cases.filter(entry_date__gte=dt)

    for case in cases:
        case.update_case()


@shared_task
def get_moscow_koap_cases_first(newest=False):
    entry_date = get_start_date(30 * 6) if newest else None
    return MoscowCasesGetter().get_cases(1, 'koap', entry_date_from=entry_date)


@shared_task
def get_moscow_koap_cases_second(newest=False):
    entry_date = get_start_date(30 * 6) if newest else None
    return MoscowCasesGetter().get_cases(2, 'koap', entry_date_from=entry_date)


@shared_task
def get_moscow_uk_cases_first(newest=False):
    entry_date = get_start_date(30 * 6) if newest else None
    return MoscowCasesGetter().get_cases(1, 'uk', entry_date_from=entry_date)


@shared_task
def get_moscow_uk_cases_second(newest=False):
    entry_date = get_start_date(30 * 6) if newest else None
    return MoscowCasesGetter().get_cases(2, 'uk', entry_date_from=entry_date)


@shared_task
def get_moscow_cases(newest=False):
    callback = group_moscow_cases.si().set(queue="grouper")
    header = []

    header += [get_moscow_koap_cases_first.si(newest=newest).set(queue="other"),
               get_moscow_koap_cases_second.si(newest=newest).set(queue="other"),
               get_moscow_uk_cases_first.si(newest=newest).set(queue="other"),
               get_moscow_uk_cases_second.si(newest=newest).set(queue="other")
               ]

    result = chord(header)(callback)
    with allow_join_result():
        result.get()


@shared_task
def get_koap_cases_first(courts, newest=False):
    entry_date = get_start_date(30 * 6) if newest else None
    return RFCasesGetter('koap').get_cases(1, courts, entry_date_from=entry_date)


@shared_task
def get_koap_cases_second(courts, newest=False):
    entry_date = get_start_date(30 * 6) if newest else None
    return RFCasesGetter('koap').get_cases(2, courts, entry_date_from=entry_date)


@shared_task
def get_uk_cases_first(courts, newest=False):
    entry_date = get_start_date(30 * 6) if newest else None
    return RFCasesGetter('uk').get_cases(1, courts, entry_date_from=entry_date)


@shared_task
def get_uk_cases_second(courts, newest=False):
    entry_date = get_start_date(30 * 6) if newest else None
    return RFCasesGetter('uk').get_cases(2, courts, entry_date_from=entry_date)


@shared_task
def fix_chunk(ids):
    for id in ids:
        case = Case.objects.get(id=id)

        case.update_case()

        try:
            # if case.type == 1:
            case.process_result_text()
        except Exception as e:
            # raise
            print(e, 'error', case.get_admin_url())


@shared_task
def fix_moscow_cases():
    cases = Case.objects.filter(result_text='', type=1, court__region=77)
    cases_ids = cases.values_list('id', flat=True)
    print(cases_ids, 'cases_ids')

    chunked_cases = chunks(cases_ids, 10)
    for chunk in chunked_cases:
        fix_chunk.s(chunk).apply_async(queue="other")


@shared_task
def update_spb():
    spb_courts = Court.objects.filter(region=78).values_list('id', flat=True)
    for court in spb_courts:
        update_cases_by_court.s(court).apply_async(queue="other")


@shared_task
def group_all():
    for region in [x for x in dict(region_choices).keys() if x not in [77, 78]]:
        group_by_region.s(region).apply_async(queue="grouper")
