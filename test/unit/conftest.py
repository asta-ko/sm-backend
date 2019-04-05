import pytest

from oi_sud.codex.models import CodexArticle
from oi_sud.courts.parser import courts_parser


@pytest.fixture()
def courts():
    courts_parser.save_courts(limit=1)

@pytest.fixture()
def better_courts():
   court_dicts = [
       {'url':'https://krv--spb.sudrf.ru', 'title':'Кировский районный суд', 'phone_numbers':['-'], 'region':81, 'site_type':1, 'type':2},
       #{'url':'https://bezhecky--twr.sudrf.ru', 'title':'Бежецкий районный суд', 'phone_numbers':['-'], 'region':1, 'site_type':2, 'type':0, 'vn_kod':'69RS0002'}
   ]
   for d in court_dicts:
       courts_parser.save_court(d)

@pytest.fixture()
def koap_articles():
    CodexArticle.objects.bulk_create(
        [CodexArticle(article_number='19.3', part=1, codex='koap'), CodexArticle(article_number='20.33', codex='koap')])