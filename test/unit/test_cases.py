import pytest
from oi_sud.cases.parser import RFCasesParser
from oi_sud.cases.models import Case
from oi_sud.cases.management.commands.get_admin_cases_from_spb_courts import Command as SpbCourtsCommand

@pytest.mark.django_db
def test_rf_parser_koap_first_instance(better_courts, koap_articles):

    p = RFCasesParser(codex='koap')
    p.get_cases_first_instance()
    assert len(Case.objects.all())
    assert False

@pytest.mark.django_db
def test_rf_parser_update(better_courts, koap_articles, settings):
    settings.USE_TZ = True
    settings.TIME_ZONE = 'Europe/Moscow'
    assert settings.USE_TZ
    p = RFCasesParser(codex='koap')
    p.get_cases_first_instance()
    assert len(Case.objects.all())
    p.update_cases()
    assert False

@pytest.mark.django_db
def test_rf_parser_uk_first_instance(better_courts, uk_articles):

    p = RFCasesParser(codex='uk')
    p.get_cases_first_instance()
    assert len(Case.objects.all())

@pytest.mark.django_db
def test_spb_courts_command(better_courts, koap_articles):
    SpbCourtsCommand().handle()
    assert len(Case.objects.all())

@pytest.mark.django_db
def test_case_serialization(better_courts, koap_articles):
    SpbCourtsCommand().handle()
    assert len(Case.objects.all())
    print(Case.objects.first().serialize())
    assert False
