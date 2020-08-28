import pytest

from oi_sud.cases.models import Case, CaseEvent
from oi_sud.cases.parsers.moscow import MoscowParser, MoscowCasesGetter
from oi_sud.codex.models import CodexArticle


@pytest.mark.skip
@pytest.mark.django_db
def test_moscow_getter(moscow_courts, koap_articles):
    MoscowCasesGetter().get_cases(1, 'koap', articles_list=['20.2 ч.5'])
    assert len(Case.objects.all())
    assert (len(CaseEvent.objects.all()))


@pytest.mark.skip
@pytest.mark.django_db
def test_save_case(moscow_courts, koap_articles):
    cases_urls = [
        'https://mos-gorsud.ru/rs/timiryazevskij/services/cases/admin/details/4ff27edb-bf19-4526-ac73-ff89095cf666',
        'https://www.mos-gorsud.ru/rs/nikulinskij/services/cases/admin/details/2163d66f-6364-4290-986f-98ee6b16b658']
    url = 'https://mos-gorsud.ru/mgs/search?courtAlias=&uid=&instance=1&processType=3&codex=ст.+19.34%2C+Ч.2'
    # cases_urls = [
    #     'https://mos-gorsud.ru/rs/meshchanskij/services/cases/admin/'
    #     'details/e759cbf7-cacd-4642-91c1-7a8479cfe270?documentMainArticle='
    #     '%D1%81%D1%82.+19.34%2C+%D0%A7.2&formType=fullForm',
    #     'https://mos-gorsud.ru/rs/tverskoj/services/cases/admin/'
    #     'details/c694e8b1-d345-4933-af40-25a3ad4ba819?'
    #     'documentMainArticle=%D1%81%D1%82.+19.34%2C+%D0%A7.2&formType=fullForm']
    article = CodexArticle.objects.filter(article_number=19.34, part=2).first()
    MoscowParser(url=url, stage=1, codex='koap', article=article).save_cases(urls=cases_urls)
    assert (len(Case.objects.all()) == 2)



@pytest.mark.skip
@pytest.mark.django_db
def test_correct_result_text_1inst(moscow_courts, koap_articles):
    url = 'https://mos-gorsud.ru/rs/meshchanskij/services/cases/admin/details/ff082d8f-d712-4661-b6f0-165e7c11b7df'
    case_info = MoscowParser(stage=1).get_raw_case_information(url)
    print(case_info)
    assert case_info
    assert case_info['events'] != []
    assert case_info['result_text'] != ''
    assert 'без удовлетворения' not in case_info['result_text']

@pytest.mark.skip
@pytest.mark.django_db
def test_correct_result_text_2inst(moscow_courts, koap_articles):
    url = 'https://mos-gorsud.ru/mgs/services/cases/review-not-yet/details/a0d44509-e1ce-41ad-af55-542d164c3766'
    case_info = MoscowParser(stage=2).get_raw_case_information(url)
    print(case_info)
    assert case_info
    assert case_info['events'] != []
    assert case_info['result_text'] != ''
    assert 'без удовлетворения' in case_info['result_text']

@pytest.mark.skip
@pytest.mark.django_db
def test_correct_result_text_1inst(moscow_courts, koap_articles):
    url = 'https://mos-gorsud.ru/rs/meshchanskij/services/cases/admin/details/ff082d8f-d712-4661-b6f0-165e7c11b7df'
    case_info = MoscowParser(stage=1).get_raw_case_information(url)
    print(case_info)
    assert case_info
    assert case_info['events'] != []
    assert case_info['result_text'] != ''
    assert 'без удовлетворения' not in case_info['result_text']


@pytest.mark.skip
@pytest.mark.django_db
def test_correct_result_text_2inst(moscow_courts, koap_articles):
    url = 'https://mos-gorsud.ru/mgs/services/cases/review-not-yet/details/a0d44509-e1ce-41ad-af55-542d164c3766'
    case_info = MoscowParser(stage=2).get_raw_case_information(url)
    print(case_info)
    assert case_info
    assert case_info['events'] != []
    assert case_info['result_text'] != ''
    assert 'без удовлетворения' in case_info['result_text']


@pytest.mark.skip
@pytest.mark.django_db
def test_get_raw_case_info(moscow_courts, koap_articles):
    url = 'https://www.mos-gorsud.ru/rs/nikulinskij/services/cases/admin/details/2163d66f-6364-4290-986f-98ee6b16b658'
    # url = 'https://mos-gorsud.ru/rs/timiryazevskij/services/cases/admin/details/4ff27edb-bf19-4526-ac73-ff89095cf666'#'https://mos-gorsud.ru/rs/timiryazevskij/services/cases/admin/details/0e45130b-8365-4c45-9279-ed69af0c6552'#'https://mos-gorsud.ru/rs/tverskoj/services/cases/admin/details/' \
    # 'c694e8b1-d345-4933-af40-25a3ad4ba819?documentMainArticle=%D1%81%D1%82.+19.34%2C+%D0%A7.2&formType=fullForm'
    case_info = MoscowParser(stage=1).get_raw_case_information(url)
    print(case_info['defenses'])
    assert case_info
    assert case_info['events'] != []
    assert case_info['result_text'] != ''


@pytest.mark.skip
@pytest.mark.django_db
def test_urls_getter(koap_articles):
    url = 'https://mos-gorsud.ru/mgs/search?courtAlias=&uid=&instance=1&processType=3&codex=ст.+19.34%2C+Ч.2'
    article = CodexArticle.objects.filter(article_number=19.34, part=2).first()
    urls = MoscowParser(url=url, stage=1, codex='koap', article=article).get_all_cases_urls(limit_pages=True)
    assert len(urls)
