from datetime import timedelta

import requests


from celery import shared_task
from django.conf import settings
from django.utils import timezone

from oi_sud.core.consts import region_choices
from oi_sud.courts.models import Court
from oi_sud.cases.parser import RFCasesParser
from oi_sud.core.utils import chunks
from celery_once import QueueOnce

@shared_task(base=QueueOnce, once={'graceful': True})
def main_get_koap_cases():
    # for region in region_choices:
    #     region_courts = Court.objects.filter(region=region[0])
    #     chunked_courts = chunks(region_courts, 10)
    #     for chunk in chunked_courts:
    #         for court in chunk
    chunked_courts = chunks(Court.objects.all().order_by('region').values_list('id', flat=True), 10)
    for chunk in chunked_courts:
        get_koap_cases_first.s(chunk).apply_async(queue='other')
        get_koap_cases_second.s(chunk).apply_async(queue='other')

@shared_task(base=QueueOnce, once={'graceful': True})
def main_get_uk_cases():
    chunked_courts = chunks(Court.objects.all().order_by('region').values_list('id', flat=True), 10)
    for chunk in chunked_courts:
        get_uk_cases_first.s(chunk).apply_async(queue='other')
        get_uk_cases_second.s(chunk).apply_async(queue='other')


@shared_task
def get_koap_cases_first(courts):
    RFCasesParser('koap').get_cases(1, courts)

@shared_task
def get_uk_cases_first(courts):
    RFCasesParser('uk').get_cases(1, courts)

@shared_task
def get_koap_cases_second(courts):
    RFCasesParser('koap').get_cases(2, courts)

@shared_task
def get_uk_cases_second(courts):
    RFCasesParser('uk').get_cases(2, courts)



