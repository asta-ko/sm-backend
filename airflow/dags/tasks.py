import os
from datetime import datetime, timedelta


def django_init():
    settings_file_name = 'tasks_airflow'
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"oi_sud.config.{settings_file_name}")

    try:
        import django
        django.setup()
    except:
        pass


def collect_rf_cases(court=None, instance=None, codex=None, date_from=None, date_to=None, *args, **kwargs):
    from oi_sud.cases.scraper.rf import rf_sc
    if not date_from:
        dt = datetime.now() - timedelta(days=30)
        start_from = dt.strftime('%d.%m.%Y')
    params = {'entry_date_from': date_from, 'entry_date_to': date_to}
    urls_data = rf_sc.get_cases_urls_by_court(court, params, instance, codex)
    rf_sc.save_parquet_from_court_urls(urls_data, filepath='/data/scraped/')


def parse_rf_cases(court=None, instance=None, codex=None, *args, **kwargs):
    from oi_sud.cases.scraper.rf import rf_sc
    rf_sc.save_cases_from_parquet(court.region, court, codex, instance, None, filepath='/data/scraped/')


def collect_moscow_cases(court=None, instance=None, codex=None, date_from=None, date_to=None, *args, **kwargs):
    from oi_sud.cases.scraper.moscow import moscow_sc
    if not date_from:
        dt = datetime.now() - timedelta(days=30)
        date_from = dt.strftime('%d.%m.%Y')
    params = {'entry_date_from': date_from, 'entry_date_to': date_to}
    urls_data = moscow_sc.get_cases_urls_by_court(court, params, instance, codex)
    moscow_sc.save_parquet_from_court_urls(urls_data, filepath='/data/scraped/')


def parse_moscow_cases(court=None, instance=None, codex=None, year=None, *args, **kwargs):
    from oi_sud.cases.scraper.moscow import moscow_sc
    # court = court.title.split(' (')[0]
    moscow_sc.save_cases_from_parquet(77, court, codex, instance, None, filepath='/data/scraped/')


def group_cases(region, *args, **kwargs):
    from oi_sud.cases.grouper import grouper
    grouper.group_cases(region=region)


def mark_risk_group(region, *args, **kwargs):
    from oi_sud.cases.models import Defendant
    for defendant in Defendant.objects.filter(region=region):
        defendant.risk_group = defendant.is_in_risk_group()
        defendant.save()
