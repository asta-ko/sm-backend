from celery import chord
from celery import shared_task
from celery.result import allow_join_result

from oi_sud.cases.grouper import grouper
from oi_sud.cases.models import Case
from oi_sud.cases.parsers.rf import RFCasesGetter
from oi_sud.core.consts import region_choices
from oi_sud.core.utils import chunks
from oi_sud.courts.models import Court

#
# class progress_chord(chord):
#
#     def __call__(self, body=None, **kwargs):
#         _chord = self.type
#         print(body)
#         body = (body or self.kwargs['body']).clone()
#         kwargs = dict(self.kwargs, body=body, **kwargs)
#         if _chord.app.conf.CELERY_ALWAYS_EAGER:
#             return self.apply((), kwargs)
#         callback_id = body.options.setdefault('task_id', uuid())
#         r= _chord(**kwargs)
#         return _chord.AsyncResult(callback_id), r


@shared_task  # (base=QueueOnce, once={'graceful': True})
def main_get_cases():
    for region in region_choices:
        get_cases_from_region.s(region=region[0]).apply_async(queue='main')


@shared_task(bind=True)
def get_cases_from_region(self, region=78):
    # progress_recorder = ProgressRecorder(self)
    callback = group_by_region.si(region=region).set(queue="other")
    header = []

    region_courts = Court.objects.filter(region=region)
    chunked_courts = chunks(region_courts.values_list('id', flat=True), 10)

    for chunk in chunked_courts:
        header += [get_koap_cases_first.si(chunk).set(queue="other"),
                   get_koap_cases_second.si(chunk).set(queue="other"),
                   get_uk_cases_first.si(chunk).set(queue="other"),
                   get_uk_cases_second.si(chunk).set(queue="other")
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
def update_cases(court_id):
    court = Court.objects.get(pk=court_id)
    cases = Case.objects.filter(court=court)
    for case in cases:
        case.update_case()


@shared_task
def get_koap_cases_first(courts):
    RFCasesGetter('koap').get_cases(1, courts)
    return True


@shared_task
def get_koap_cases_second(courts):
    RFCasesGetter('koap').get_cases(2, courts)
    return True


@shared_task
def get_uk_cases_first(courts):
    RFCasesGetter('uk').get_cases(1, courts)
    return True


@shared_task
def get_uk_cases_second(courts):
    RFCasesGetter('uk').get_cases(2, courts)
    return True
