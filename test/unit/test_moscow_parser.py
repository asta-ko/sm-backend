import pytest

from oi_sud.cases.models import Case
from oi_sud.cases.management.commands.get_admin_cases_from_spb_courts import Command as SpbCourtsCommand
from oi_sud.cases.parsers.moscow import MoscowParser, MoscowCasesGetter

@pytest.mark.skip
@pytest.mark.django_db
def test_moscow_getter(koap_articles):
    MoscowCasesGetter().get_cases(1, 'koap')
    assert False

#
# def test_urls_getter():
#
#     p = MoscowParser(url=url, stage=instance)
#
