import pytest
import os

from oi_sud.cases.scraper.rf import RFScraper
from oi_sud.cases.scraper.moscow import MoscowScraper
from oi_sud.cases.models import Case


@pytest.mark.skip
@pytest.mark.django_db
def test_get_rf_urls(rf_courts, koap_articles):
    sc = RFScraper()
    params = {'entry_date_from':'19.09.2020'}
    urls_data = sc.get_cases_urls_by_court(rf_courts[0], params, 1, 'koap')
    print(urls_data)
    assert len(urls_data['cases_urls'])

@pytest.mark.skip
@pytest.mark.django_db
def test_get_moscow_urls(moscow_courts, koap_articles):
    sc = MoscowScraper()
    params = {'entry_date_from':'24.08.2020'}
    urls_data = sc.get_cases_urls_by_court(moscow_courts[0], params, 1, 'koap')
    print(urls_data)
    assert len(urls_data['cases_urls'])

@pytest.mark.skip
@pytest.mark.django_db
def test_save_parquet_rf_urls(rf_courts, koap_articles):
    sc = RFScraper()
    params = {'entry_date_from':'24.08.2020'}
    urls_data = sc.get_cases_urls_by_court(rf_courts[0], params, 1, 'koap')
    sc.save_parquet_from_court_urls(urls_data, '/tmp/tests/parquet/')
    print(urls_data)
    assert len(urls_data['cases_urls'])

@pytest.mark.skip
@pytest.mark.django_db
def test_save_parquet_moscow_urls(moscow_courts, koap_articles):
    sc = MoscowScraper()
    params = {'entry_date_from':'24.08.2020'}
    urls_data = sc.get_cases_urls_by_court(moscow_courts[0], params, 1, 'koap')
    sc.save_parquet_from_court_urls(urls_data, '/tmp/tests/parquet/')
    print(urls_data)
    assert len(urls_data['cases_urls'])

@pytest.mark.skip
@pytest.mark.django_db
def test_save_rf_cases(rf_courts, koap_articles):
    sc = RFScraper()
    params = {'entry_date_from': '20.09.2020'}
    urls_data = sc.get_cases_urls_by_court(rf_courts[0], params, 1, 'koap')
    filepath = '/tmp/tests/parquet/'
    sc.save_parquet_from_court_urls(urls_data, filepath=filepath)
    sc.save_cases_from_parquet(rf_courts[0].region, rf_courts[0], 'koap', 1, None, filepath=filepath)
    print(Case.objects.all())


#@pytest.mark.skip
@pytest.mark.django_db
def test_save_moscow_cases(moscow_courts, koap_articles):
    sc = MoscowScraper()
    params = {'entry_date_from': '20.09.2020'}
    urls_data = sc.get_cases_urls_by_court(moscow_courts[0], params, 1, 'koap')
    filepath = '/tmp/tests/parquet/'
    sc.save_parquet_from_court_urls(urls_data, filepath=filepath)
    sc.save_cases_from_parquet(77, moscow_courts[0], 'koap', 1, None, filepath=filepath)
    print(Case.objects.all())
