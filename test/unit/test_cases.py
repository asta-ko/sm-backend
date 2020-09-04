import pytest
from django.utils import timezone
from oi_sud.cases.models import Case, ClonableCase
from oi_sud.cases.parsers.rf import FirstParser
from oi_sud.courts.models import Court


@pytest.mark.skip
@pytest.mark.django_db
def test_merge_multiple_duplicates(rf_courts, koap_articles, mocker):
    court = Court.objects.filter(title='Выборгский районный суд').first()

    url = 'https://vbr--spb.sudrf.ru/modules.php?name=sud_delo&name_op=case&case_id=401366335&case_uid=f6a0de4d-819c-4458-9577-0565645e9c89&result=0&new=&delo_id=1502001&srv_num=1'  # 'https://oktibrsky--spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=419372260&case_uid=867f0e26-b0ea-40ec-8d30-be8f8f1fca9c&delo_id=1500001'
    FirstParser(court=court, stage=2, codex='koap').save_cases(urls=[url, ])
    old_case_query = ClonableCase.objects.all()
    old_case_query.update(**{'url': 'example_url_1', 'result_text': 'result_text_1', 'appeal_date': timezone.now()})
    another_old_case = old_case_query.first().make_clone(
        attrs={'url': 'example_url_2', 'result_text': 'example_result_text_2', 'protocol_number': 'example_number'})
    FirstParser(court=court, stage=2, codex='koap').save_cases(urls=[url, ])
    new_case = ClonableCase.objects.first()
    assert new_case
    assert ClonableCase.objects.count() == 1
    assert new_case.url == url
    assert new_case.result_text == 'example_result_text_2'
    assert new_case.protocol_number == '7'


@pytest.mark.skip
@pytest.mark.django_db
def test_double_processing_identical(rf_courts, koap_articles):
    court = Court.objects.filter(title='Выборгский районный суд').first()
    url = 'https://vbr--spb.sudrf.ru/modules.php?name=sud_delo&name_op=case&case_id=401366335&case_uid=f6a0de4d-819c-4458-9577-0565645e9c89&result=0&new=&delo_id=1502001&srv_num=1'  # 'https://oktibrsky--spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=419372260&case_uid=867f0e26-b0ea-40ec-8d30-be8f8f1fca9c&delo_id=1500001'
    FirstParser(court=court, stage=2, codex='koap').save_cases(urls=[url, ])
    old_case_query = Case.objects.all()
    old_case_query.update(**{'url': 'example_url_1'})

    FirstParser(court=court, stage=2, codex='koap').save_cases(
        urls=[url, ])  # save a new identical case but with another url

    new_case = Case.objects.first()
    assert new_case
    assert Case.objects.count() == 1
    assert new_case.url == url


@pytest.mark.skip
@pytest.mark.django_db
def test_double_processing_non_identical(rf_courts, koap_articles):
    court = Court.objects.filter(title='Выборгский районный суд').first()
    url = 'https://vbr--spb.sudrf.ru/modules.php?name=sud_delo&name_op=case&case_id=401366335&case_uid=f6a0de4d-819c-4458-9577-0565645e9c89&result=0&new=&delo_id=1502001&srv_num=1'  # 'https://oktibrsky--spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=419372260&case_uid=867f0e26-b0ea-40ec-8d30-be8f8f1fca9c&delo_id=1500001'
    FirstParser(court=court, stage=2, codex='koap').save_cases(urls=[url, ])
    old_case_query = Case.objects.all()
    old_case_query.update(**{'url': 'example_url_1', 'protocol_number': 'example_number'})
    FirstParser(court=court, stage=2, codex='koap').save_cases(
        urls=[url, ])  # save a new non identical case

    new_case = Case.objects.first()
    assert new_case
    assert new_case.url == url
    assert new_case.protocol_number == '7'


@pytest.mark.skip
@pytest.mark.django_db
def test_non_double_processing(rf_courts, koap_articles):
    court = Court.objects.filter(title='Выборгский районный суд').first()
    court2 = Court.objects.filter(title='Кировский районный суд').first()
    urls = [
        'https://vbr--spb.sudrf.ru/modules.php?name=sud_delo&name_op=case&case_id=401366335&case_uid=f6a0de4d-819c-4458-9577-0565645e9c89&result=0&new=&delo_id=1502001&srv_num=1',
        'https://krv--spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=422424346&case_uid=cdda91f9-80db-41e3-92dc-fe32f63ee605&delo_id=1500001']
    FirstParser(court=court, stage=2, codex='koap').save_cases(urls=[urls[0], ])
    FirstParser(court=court2, stage=1, codex='koap').save_cases(urls=[urls[1], ])
    assert (Case.objects.count() == 2)
    assert (Case.duplicates.count() == 0)


@pytest.mark.skip
@pytest.mark.django_db
def test_moved_finder(rf_courts, koap_articles):
    url = 'https://vbr--spb.sudrf.ru/modules.php?name=sud_delo&name_op=case&case_id=401366335&case_uid=f6a0de4d-819c-4458-9577-0565645e9c89&result=0&new=&delo_id=1502001&srv_num=1'  # 'https://oktibrsky--spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=419372260&case_uid=867f0e26-b0ea-40ec-8d30-be8f8f1fca9c&delo_id=1500001'

    FirstParser(court=Court.objects.filter(title='Выборгский районный суд').first(), stage=2, codex='koap').save_cases(
        urls=[url, ])
    case = Case.objects.first()
    assert (case)
    assert url != case.search_for_new_url()


def save_from_raw(self, raw_case_data):
    serialized_case_data = self.serialize_data(raw_case_data)
    return Case.objects.create_case_from_data(serialized_case_data)


FirstParser.save_from_raw = save_from_raw


@pytest.mark.skip
@pytest.mark.django_db
def test_update_case_correct_defenses(case_raw_dict, rf_courts):
    parser = FirstParser(court=Court.objects.filter(title='Выборгский районный суд').first(), stage=2, codex='koap')
    error_defense_advocate_name = {'defendant': 'Рассохин А.А.', 'codex_articles': ''}
    error_defense_prosecutor_name = {'defendant': 'Ильин Н.В.', 'codex_articles': ''}
    case_raw_dict['defenses'].append(error_defense_advocate_name)
    case_raw_dict['defenses'].append(error_defense_prosecutor_name)
    c = parser.save_from_raw(case_raw_dict)
    c.update_case()
    # assert len(c.defenses.all()) == 1 #WTF
    assert len(c.get_advocates()) == 2
    assert len(c.get_prosecutors()) == 2


@pytest.mark.skip
@pytest.mark.django_db
def test_update_case_add(case_raw_dict, rf_courts):
    parser = FirstParser(court=Court.objects.filter(title='Выборгский районный суд').first(), stage=2, codex='koap')
    del case_raw_dict['case_uid']
    parser.save_from_raw(case_raw_dict)
    c_old = Case.objects.first()
    c_old.update_case()
    assert c_old.case_uid
    assert c_old.updated_at


@pytest.mark.skip
@pytest.mark.django_db
def test_update_case_change(case_raw_dict, rf_courts):
    parser = FirstParser(court=Court.objects.filter(title='Выборгский районный суд').first(), stage=2, codex='koap')
    case_raw_dict['case_uid'] = 'blabla'
    parser.save_from_raw(case_raw_dict)
    c_old = Case.objects.first()
    c_old.update_case()
    assert c_old.case_uid != 'blabla'


@pytest.mark.skip
@pytest.mark.django_db
def test_update_case_dont_remove(case_raw_dict, rf_courts):
    parser = FirstParser(court=Court.objects.filter(title='Выборгский районный суд').first(), stage=2, codex='koap')
    case_raw_dict['appeal_result'] = 'blabla'
    parser.save_from_raw(case_raw_dict)
    c_old = Case.objects.first()
    c_old.update_case()
    assert c_old.appeal_result == 'blabla'


@pytest.mark.skip
@pytest.mark.django_db
def test_update_case_was_moved(moved_case_raw_dict, rf_courts):
    c_old = FirstParser(stage=1, codex='koap',
                        court=Court.objects.filter(title='Невский районный суд').first()).save_from_raw(
        moved_case_raw_dict)
    c_old.update_case()
    assert Case.objects.count() == 1
    print(c_old.url, 'NEW_URL')
    assert c_old.url != moved_case_raw_dict['url']


def process_duplicates(self, new_case):
    return


@pytest.mark.skip
@pytest.mark.django_db
def test_update_case_was_moved_but_exists_in_db_non_identical(moved_case_raw_dict, moved_case_raw_dict_new, rf_courts):
    FirstParser.process_duplicates = process_duplicates
    c_new = FirstParser(stage=1, codex='koap',
                        court=Court.objects.filter(title='Невский районный суд').first()).save_from_raw(
        moved_case_raw_dict_new)
    moved_case_raw_dict['defenses'].append({'defendant': "Ипатов Н.К.", "codex_articles": '20.2 ч.5'})
    c_old = FirstParser(stage=1, codex='koap',
                        court=Court.objects.filter(title='Невский районный суд').first()).save_from_raw(
        moved_case_raw_dict)
    print('saved 2 cases')
    assert Case.objects.count() == 2
    c_old.update_case()
    print('updated')
    assert Case.objects.count() == 1
    assert c_old.defenses.count() == 2
    assert c_old.url != moved_case_raw_dict['url']
    assert c_old.url == moved_case_raw_dict_new['url']


@pytest.mark.skip
@pytest.mark.django_db
def test_update_case_was_moved_but_exists_in_db(moved_case_raw_dict, moved_case_raw_dict_new, rf_courts):
    FirstParser.process_duplicates = process_duplicates
    c_new = FirstParser(stage=1, codex='koap',
                        court=Court.objects.filter(title='Невский районный суд').first()).save_from_raw(
        moved_case_raw_dict_new)
    c_old = FirstParser(stage=1, codex='koap',
                        court=Court.objects.filter(title='Невский районный суд').first()).save_from_raw(
        moved_case_raw_dict)
    assert Case.objects.count() == 2
    c_old.update_case()
    assert Case.objects.count() == 1
    assert c_old.url != moved_case_raw_dict['url']
    assert c_old.url == moved_case_raw_dict_new['url']
