import pytest
from oi_sud.cases.parser import RFCasesParser

@pytest.mark.django_db
def test_rf_parser_url_generator(better_courts, koap_articles):

    p = RFCasesParser(codex='koap')
    p.get_cases_first_instance()

