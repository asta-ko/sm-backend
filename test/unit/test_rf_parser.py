import pytest
from oi_sud.cases.models import Case, Advocate, Prosecutor
from oi_sud.cases.parsers.rf import RFCasesGetter, FirstParser, SecondParser
from oi_sud.courts.models import Court
from reversion.models import Revision


@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser_koap_first_instance(rf_courts, koap_articles):
    p = RFCasesGetter(codex='koap')
    p.get_cases(1)
    assert len(Case.objects.all())


@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser_koap_second_instance(rf_courts, koap_articles):
    RFCasesGetter('koap').get_cases(2, rf_courts)
    assert len(Case.objects.all())
    # assert False


@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser_uk_first_instance(rf_courts, uk_articles):
    p = RFCasesGetter(codex='uk')
    p.get_cases(1)
    assert len(Case.objects.all())


@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser_uk_second_instance(rf_courts, uk_articles):
    p = RFCasesGetter(codex='uk')
    p.get_cases(2)
    assert len(Case.objects.all())


@pytest.mark.skip
@pytest.mark.django_db
def test_get_raw_first():
    urls = [
        'https://vyatskopolyansky--kir.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=80099975&case_uid=6d2f602e-0770-4180-ba35-3e6790dc5a66&delo_id=1500001&nc=1']
    for url in urls:
        case_info = FirstParser().get_raw_case_information(url)


@pytest.mark.skip
@pytest.mark.django_db
def test_get_raw_second():
    urls = [
        'https://bezhecky--twr.sudrf.ru/modules.php?name=sud_delo&name_op=case&_uid=8f796b72-d312-4d7f-aba7-4f0782c78cd6&_deloId=1540006&_caseType=0&_new=0&srv_num=1&_hideJudge=0&nc=1']
    for url in urls:
        case_info = SecondParser().get_raw_case_information(url)


@pytest.mark.skip
@pytest.mark.django_db
def test_raw_case_info_first(rf_courts, koap_articles):
    url = 'https://vbr--spb.sudrf.ru/modules.php?name=sud_delo&name_op=case&case_id=401366335&case_uid=f6a0de4d-819c-4458-9577-0565645e9c89&result=0&new=&delo_id=1502001&srv_num=1'  # 'https://oktibrsky--spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=419372260&case_uid=867f0e26-b0ea-40ec-8d30-be8f8f1fca9c&delo_id=1500001'
    case_info = FirstParser().get_raw_case_information(url)

    print(case_info['defenses'])
    assert case_info
    assert case_info['events'] != []
    FirstParser(court=Court.objects.filter(title='Выборгский районный суд').first(), stage=2, codex='koap').save_cases(
        urls=[url, ])
    case = Case.objects.first()
    assert Advocate.objects.count()
    assert Prosecutor.objects.count()


@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser_update(rf_courts, koap_articles, settings):
    settings.USE_TZ = True
    settings.TIME_ZONE = 'Europe/Moscow'
    assert settings.USE_TZ
    p = RFCasesGetter(codex='koap')
    p.get_cases(1)
    assert len(Case.objects.all())
    revisions_len = len(Revision.objects.all())
    assert revisions_len
    for case in Case.objects.all():
        case.update_case()
    assert len(Revision.objects.all()) > revisions_len
    for item in Revision.objects.all():
        print(item.comment)
