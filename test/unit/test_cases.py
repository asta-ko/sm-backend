import pytest
from oi_sud.cases.parser import RFCasesParser
from oi_sud.cases.management.commands.get_admin_cases_from_spb_courts import Command as SpbCourtsCommand

@pytest.mark.django_db
def test_rf_parser_koap_first_instance(better_courts, koap_articles):

    p = RFCasesParser(codex='koap')
    p.get_cases_first_instance()

@pytest.mark.django_db
def test_rf_parser_uk_first_instance(better_courts, uk_articles):

    p = RFCasesParser(codex='uk')
    p.get_cases_first_instance()

@pytest.mark.django_db
def test_spb_courts_command(better_courts, koap_articles):
    SpbCourtsCommand().handle()
