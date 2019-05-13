from datetime import timedelta

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from oi_sud.core.consts import region_choices
from oi_sud.courts.models import Court
from oi_sud.cases.parser import RFCasesParser
from oi_sud.core.utils import chunks

@shared_task
def main_get_koap_cases(data=None):
    # for region in region_choices:
    #     region_courts = Court.objects.filter(region=region[0])
    #     chunked_courts = chunks(region_courts, 10)
    #     for chunk in chunked_courts:
    #         for court in chunk
    chunked_courts = chunks(Courts.objects.all(), 10)
    for chunk in chunked_courts:
        get_koap_cases_first.s(chunk)

@shared_task
def get_koap_cases_first(courts):
    RFCasesParser('koap').get_cases(1, courts)







