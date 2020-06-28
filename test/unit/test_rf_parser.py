import pytest
from oi_sud.cases.management.commands.get_admin_cases_from_spb_courts import Command as SpbCourtsCommand
from oi_sud.cases.models import Case, Advocate, Prosecutor
from oi_sud.cases.parsers.rf import RFCasesGetter, FirstParser, SecondParser
from oi_sud.cases.utils import parse_name
from oi_sud.courts.models import Court
from reversion.models import Revision


#@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser(rf_courts, koap_articles):
    print(rf_courts, koap_articles)
    court = Court.objects.filter(title='Кировский районный суд',region=78)
    RFCasesGetter(codex='koap').get_cases(1, courts_ids=[court[0].id], courts_limit=1)
    assert len(Case.objects.all())

#@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser_koap_first_instance(rf_courts, koap_articles):
    p = RFCasesGetter(codex='koap')
    p.get_cases(1)
    assert len(Case.objects.all())


#@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser_koap_second_instance(rf_courts, koap_articles):
    RFCasesGetter('koap').get_cases(2, rf_courts)
    assert len(Case.objects.all())
    # assert False


#@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser_uk_first_instance(rf_courts, uk_articles):
    p = RFCasesGetter(codex='uk')
    p.get_cases(1)
    assert len(Case.objects.all())


#@pytest.mark.skip
@pytest.mark.django_db
def test_rf_parser_uk_second_instance(rf_courts, uk_articles):
    p = RFCasesGetter(codex='uk')
    p.get_cases(2)
    assert len(Case.objects.all())

@pytest.mark.skip
@pytest.mark.django_db
def test_cases_saving(rf_courts, koap_articles):
    urls = ['https://vyatskopolyansky--kir.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=80099975&case_uid=6d2f602e-0770-4180-ba35-3e6790dc5a66&delo_id=1500001&nc=1']
    for url in urls:
        case_info = FirstParser().get_raw_case_information(url)


@pytest.mark.skip
@pytest.mark.django_db
def test_raw_case_info_first(rf_courts, koap_articles):
    url = 'https://vbr--spb.sudrf.ru/modules.php?name=sud_delo&name_op=case&case_id=401366335&case_uid=f6a0de4d-819c-4458-9577-0565645e9c89&result=0&new=&delo_id=1502001&srv_num=1'#'https://oktibrsky--spb.sudrf.ru/modules.php?name=sud_delo&srv_num=1&name_op=case&case_id=419372260&case_uid=867f0e26-b0ea-40ec-8d30-be8f8f1fca9c&delo_id=1500001'
    case_info = FirstParser().get_raw_case_information(url)

    print(case_info['defenses'])
    assert case_info
    assert case_info['events'] != []
    FirstParser(court=Court.objects.filter(title='Выборгский районный суд').first(), stage=2, codex='koap').save_cases(urls=[url,])
    case = Case.objects.first()
    print(case)
    print(case.get_advocates())
    print(case.get_prosecutors())
    print(Advocate.objects.all())
    print(Prosecutor.objects.all())




@pytest.mark.skip
def test_name_parser():
    names_list = ['Пиатровский Андрей Владимирович', 'Магомадов Арсен Сулейманович', 'Зинченко Нина Владимировна',
                  'Буриев Фазлиддин Сироджиддинович', 'МЕЛЕХИН ЕВГЕНИЙ ВИКТОРОВИЧ', 'БЫСТРОВ ДМИТРИЙ ВАЛЕНТИНОВИЧ',
                  'Беленькая Вероника Александровна', 'Заленский Алексей Владимирович',
                  'Крыленкова Александра Андреевна', 'Лещинский Михаил Дмитриеич', 'Овсяников Иван Александрович',
                  'Пославский Владимир Владимирович', 'Тимошин Константин Владимирович',
                  'Симигласова Надежда Анатольевна', 'Чумаков Руслан Владимирович', 'ВАН ЛЯНЮЙ',
                  'МИСТРЮКОВА ЕКАТЕРИНА ВЛАДИМИРОВНА', 'Кулитца Ксения Владимировна',
                  'Перевозчикова Екатерина Владимировна', 'Соколов Георгий Анатольевич',
                  'Петрашко Александр Владимирович', 'Новиков Сергей Дмитриевич', 'Алексеев Константин Викторович',
                  'Крисман Сергей Валерьевич', 'Малиновский Алексей Николаевич', 'Степанов Олег Ростиславович',
                  'Корабельников Сергей Михайлович', 'Гринцевич Владислав Михайлович',
                  'Крушинский Александр Валерьевич', 'Худайгулов Фаниль Фазылович', 'Кадыралиев Азирет Суюналиевич',
                  'Прокофьев Юрий Валерьевич', 'Калиненков Артем Анатольевич', 'Голубкин Иван Алексеевич',
                  'Магомедов Арсен Зубаирович', 'Фолькерт Никита Петрович', 'Мирзоев Хотам Чураевич',
                  'Эркаев Журабек Иром угли', 'Гордиенко Александр Анатольевич', 'Будников Артем Сергеевич',
                  'Модестова Надежда Владимировна', 'Малинов Владимир Евгеньевич', 'Пересторонин Юрий Аркадьевич',
                  'Харитонов Виталий Владимирович', 'Терещенков Константин Викторович',
                  'Крашенинникова Наталья Ивановна', 'Лебедев Кирилл Вячеславович', 'Скобкарёв Александр Александрович',
                  'Владимирский Алексей Олегович', 'Емельянов Александр Александрович',
                  'Асадуллаев Хаджимурад Ибрагимович', 'Осмаловский Сергей Валерьевич',
                  'Ахайлова Хадижат Хирамагомедовна', 'Елисеев Александр Александрович', 'Марталлер Вадим Евгеньевич',
                  'Федченко Владимир Анатольевич', 'Курт-Аджиева Анастасия Сергеевна', 'Шаферман Екатерина Олеговна',
                  'Скородумов Вячеслав Владимирович', 'Меркулова Елизавета Викторовна',
                  'Долгопольская Регина Михайловна', 'Пышкин Валентин Валентинович', 'Чеснокова Гульнара Ильгизовна',
                  'Соковиков Григорий Игоревич', 'Мокотов Александр Евгеньевич', 'Керимов Ренат Рефатович',
                  'Коновальцев Дмитрий Андреевич', 'Баранов Антон Александрович', 'Савельев Александр Николаевич',
                  'Мистрюкова Екатерина Владимировна', 'Литвинова Елена Александровна', 'Майстренко Алексей Николаевич',
                  'Кочергин Олег Евгеньевич', 'Скоробогатова Мария Евгеньевна', 'Генералов Валерий Владимирович',
                  'Абрамова Анна Александровна', 'Ревенков Сергей Васильевич', 'Крапошин Андрей Александрович',
                  'Верещагин Александр Алексеевич', 'Быковский Анатолий Аркадьевич', 'Дюбченко Алексей Александрович',
                  'Аршуков Михаил Владимирович', 'Федорова Екатерина Владимировна', 'Хомяков Михаил Александрович',
                  'Лобовкина Наталья Ниловна', 'Нетребина Екатерина Филлиповна', 'Мельникова Виктория Николаевна',
                  'Кузьменко Антон Викторович', 'Кривошенина Александра Дмитриевна', 'Русаков Александр Юрьевич',
                  'Красильников Владислав Анатольевич', 'ФЕДКЕВИЧ МАКЧИМ НИКОЛАЕВИЧ', 'Огарков Алексей Сергеевич',
                  'Панкратовский Максим Владимирович', 'Крисламов Александр Геннадьевич',
                  'Наследников Давид Александрович', 'Карпюк Олег Владимирович', 'ГНЕЗДИЛОВ АЛЕКСАНДР СЕРГЕЕВИЧ',
                  'Тумашевич Тахир Николаевич', 'Кузнецов Александр Викторович', 'Журавлев Алексей Рудольфович',
                  'Локьяев Константин Александрович', 'Рукавицын Александр Сергеевич',
                  'Камаров Низомиддин Имомиддинович', 'Cтаркова Александра Сергеевна',
                  'Катрановский Георгий Николаевич', 'Замалдинов Ильдар Вадимович', 'Козловский Юрий Александрович',
                  'Чепыга Сергей Николаевич', 'Дремин Михаил Сергеевич', 'Макаровский Максим Владимирович',
                  'Безденежных Иннокентий Сергеевич']
    for x in names_list:
        print(parse_name(x))


#@pytest.mark.skip
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


@pytest.mark.skip
@pytest.mark.django_db
def test_spb_courts_command(rf_courts, koap_articles):
    SpbCourtsCommand().handle()
    assert len(Case.objects.all())

