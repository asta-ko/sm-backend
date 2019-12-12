import pytest

from oi_sud.cases.models import Case, CaseEvent
from oi_sud.cases.parsers.moscow import MoscowParser, MoscowCasesGetter
from oi_sud.codex.models import CodexArticle


@pytest.mark.skip
@pytest.mark.django_db
def test_moscow_getter(moscow_courts, koap_articles):
    MoscowCasesGetter().get_cases(1, 'koap', articles_list=['19.34 ч.2'])
    assert len(Case.objects.all())


@pytest.mark.skip
@pytest.mark.django_db
def test_save_case(moscow_courts, koap_articles):
    url = 'https://mos-gorsud.ru/mgs/search?courtAlias=&uid=&instance=1&processType=3&codex=ст.+19.34%2C+Ч.2'
    cases_urls = [
        'https://mos-gorsud.ru/rs/meshchanskij/services/cases/admin/details/e759cbf7-cacd-4642-91c1-7a8479cfe270?documentMainArticle=%D1%81%D1%82.+19.34%2C+%D0%A7.2&formType=fullForm',
        'https://mos-gorsud.ru/rs/tverskoj/services/cases/admin/details/c694e8b1-d345-4933-af40-25a3ad4ba819?documentMainArticle=%D1%81%D1%82.+19.34%2C+%D0%A7.2&formType=fullForm']
    article = CodexArticle.objects.filter(article_number=19.34, part=2).first()
    MoscowParser(url=url, stage=1, codex='koap', article=article).save_cases(urls=cases_urls)
    assert (len(Case.objects.all()) == 2)
    assert (len(CaseEvent.objects.all()))


@pytest.mark.skip
@pytest.mark.django_db
def test_get_raw_case_info(moscow_courts, koap_articles):
    url = 'https://mos-gorsud.ru/rs/tverskoj/services/cases/admin/details/c694e8b1-d345-4933-af40-25a3ad4ba819?documentMainArticle=%D1%81%D1%82.+19.34%2C+%D0%A7.2&formType=fullForm'
    case_info = MoscowParser().get_raw_case_information(url)
    assert case_info


@pytest.mark.skip
@pytest.mark.django_db
def test_urls_getter(koap_articles):
    url = 'https://mos-gorsud.ru/mgs/search?courtAlias=&uid=&instance=1&processType=3&codex=ст.+19.34%2C+Ч.2'
    article = CodexArticle.objects.filter(article_number=19.34, part=2).first()
    urls = MoscowParser(url=url, stage=1, codex='koap', article=article).get_all_cases_urls(limit_pages=True)
    print(urls)
    assert len(urls)
