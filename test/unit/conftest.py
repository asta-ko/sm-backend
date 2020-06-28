import pytest

from oi_sud.codex.models import CodexArticle
from oi_sud.courts.parser import courts_parser
from oi_sud.courts.models import Court


@pytest.fixture()
def courts():
    courts_parser.save_courts(limit=1)


@pytest.fixture()
def moscow_courts():
    court_dicts = [
        {'url': 'https://mos-gorsud.ru/rs/cheryomushkinskij', 'title': 'Черемушиниский районный суд', 'phone_numbers': ['-'],
         'region': 77,
         'site_type': 3, 'type': 2},
    ]
    for d in court_dicts:
        courts_parser.save_court(d)


@pytest.fixture()
def rf_courts():
    court_dicts = [
        # {'url': 'https://musliumovsky--tat.sudrf.ru', 'title': 'Муслимовский районный суд',
        # 'phone_numbers': ['-'],'region': 78,'site_type': 1, 'type': 2},
        {'url': 'https://krv--spb.sudrf.ru', 'title': 'Кировский районный суд', 'phone_numbers': ['-'], 'region': 78,
         'site_type': 1, 'type': 2, 'unprocessed_cases_urls':[]},
        #{'url': 'https://vbr--spb.sudrf.ru', 'title': 'Выборгский районный суд', 'phone_numbers': ['-'], 'region': 78,
        # 'site_type': 1, 'type': 2, 'unprocessed_cases_urls':[]},
        #{'url':'http://nvs.spb.sudrf.ru','title':'Невский районный суд','phone_numbers': ['-'], 'region': 78,
        # 'site_type': 1, 'type': 2, 'unprocessed_cases_urls':[]},
        {'url': 'https://bezhecky--twr.sudrf.ru', 'title': 'Бежецкий районный суд', 'phone_numbers': ['-'], 'region': 1,
         'site_type': 2, 'type': 0, 'vn_kod': '69RS0002', 'unprocessed_cases_urls':[]},
        # {'url':'https://gvs--spb.sudrf.ru/','title':'Военный суд', 'phone_numbers': ['-'], 'region': 78,
        #  'site_type': 1, 'type': 2, 'unprocessed_cases_urls':[]}
    ]
    for d in court_dicts:
        courts_parser.save_court(d)
    return Court.objects.all()


@pytest.fixture()
def koap_articles():
    CodexArticle.objects.bulk_create(
        [CodexArticle(article_number='19.3', part=1, codex='koap'),
         CodexArticle(article_number='5.38', codex='koap'),
         CodexArticle(article_number='19.34', part=2, codex='koap'),])
         #CodexArticle(article_number='20.2',part=5,codex='koap')])
    return CodexArticle.objects.all()


@pytest.fixture()
def uk_articles():
    CodexArticle.objects.bulk_create(
        [CodexArticle(article_number='318', part=1, codex='uk'), CodexArticle(article_number='319', codex='uk')])
    return CodexArticle.objects.all()

@pytest.fixture()
def case_raw_dict():
    return {'case_number': '12-245/2020', 'url': 'https://vbr--spb.sudrf.ru/modules.php?name=sud_delo&name_op=case&case_id=401366335&case_uid=f6a0de4d-819c-4458-9577-0565645e9c89&result=0&new=&delo_id=1502001&srv_num=1', 'case_uid': '78RS0002-01-2019-009411-25', 'entry_date': '17.02.2020', 'protocol_number': '7', 'events': [{'type': 'Материалы переданы в производство судье', 'date': '17.02.2020', 'time': '17:19'}, {'type': 'Судебное заседание', 'date': '26.03.2020', 'time': '13:45', 'courtroom': '№342', 'result': 'Заседание отложено'}, {'type': 'Судебное заседание', 'date': '04.06.2020', 'time': '14:15', 'courtroom': '№342'}], 'defenses': [{'defendant': 'Шайдуров Леонид Александрович', 'codex_articles': 'КоАП: ст. 20.2 ч.5', 'advocates': ['Рассохин А.А.'], 'prosecutors': ['Ильин Н.В.', 'Шляков никита Вадимович']}], 'defendants_hidden': False}

@pytest.fixture()
def moved_case_raw_dict():
    return {'events':[], 'defenses':[{'defendant':'Похильчук К.В.','codex_articles': 'КоАП: ст. 20.2 ч.5'}], 'case_number': '5-743/2019', 'entry_date': '08.07.2019', 'case_uid': '78RS0015-01-2018-007677-60', 'protocol_number': '018138',  'result_type': 'Вынесено определение о возвращении протокола об АП и др. материалов дела в орган, долж. лицу ... в случае составления протокола и оформления других материалов дела неправомочными лицами, ...', 'type': 1, 'stage': 1,  'url': 'http://nvs.spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=364909699&case_uid=1d0c29aa-d70d-4e26-b986-90bcc3e6f308&delo_id=1500001','codex_articles': 'КоАП: ст. 20.2 ч.5'}

@pytest.fixture()
def moved_case_raw_dict_new():
    return {'case_number': '5-743/2019', 'url': 'http://nvs.spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=429323953&case_uid=1d0c29aa-d70d-4e26-b986-90bcc3e6f308&delo_id=1500001', 'case_uid': '78RS0015-01-2018-007677-60', 'entry_date': '09.07.2019', 'protocol_number': '018138', 'judge': 'Лыкова Светлана Александровна', 'result_date': '19.07.2019', 'result_type': 'Вынесено определение о возвращении протокола об АП и др. материалов дела в орган, долж. лицу ... в случае составления протокола и оформления других материалов дела неправомочными лицами, ...', 'events': [{'type': 'Передача дела судье', 'date': '10.07.2019', 'time': '15:03'}, {'type': 'Подготовка дела к рассмотрению', 'date': '19.07.2019', 'time': '12:36', 'result': 'Возвращено без рассмотрения'}, {'type': 'Материалы дела сданы в отдел судебного делопроизводства', 'date': '02.08.2019', 'time': '15:45'}], 'defenses': [{'defendant': 'ПОХИЛЬЧУК КОНСТАНТИН ВАЛЕНТИНОВИЧ', 'codex_articles': 'КоАП: ст. 20.2 ч.5', 'advocates': ['Семёнов Даниил Александрович'], 'prosecutors': []}], 'defendants_hidden': False}

#
# @pytest.fixture()
# def all_articles():
#     from django.core.management import call_command
#     call_command('loaddata', 'codex.json')


# @pytest.fixture()
# def older_case():
#     court = courts_parser.save_court({'url': 'https://vbr--spb.sudrf.ru', 'title': 'Выборгский районный суд', 'phone_numbers': ['-'], 'region': 78,
#          'site_type': 1, 'type': 2, 'unprocessed_cases_urls':[]})
#     url = 'https://vbr--spb.sudrf.ru/modules.php?name=sud_delo&name_op=case&case_id=401366335&case_uid=f6a0de4d-819c-4458-9577-0565645e9c89&result=0&new=&delo_id=1502001&srv_num=1'  # 'https://oktibrsky--spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=419372260&case_uid=867f0e26-b0ea-40ec-8d30-be8f8f1fca9c&delo_id=1500001'
#     FirstParser(court=court, stage=2, codex='koap').save_cases(urls=[url, ])
#     case = Case.objects.first()
#     case.res
