region_choices = (
    (1, 'Республика Адыгея'),
    (2, 'Республика Башкортостан'),
    (3, 'Республика Бурятия'),
    (4, 'Республика Алтай'),
    (5, 'Республика Дагестан'),
    (6, 'Республика Ингушетия'),
    (7, 'Кабардино-Балкарская Республика'),
    (8, 'Республика Калмыкия'),
    (9, 'Республика Карачаево-Черкесия'),
    (10, 'Республика Карелия'),
    (11, 'Республика Коми'),
    (12, 'Республика Марий Эл'),
    (13, 'Республика Мордовия'),
    (14, 'Республика Саха (Якутия)'),
    (15, 'Республика Северная Осетия-Алания'),
    (16, 'Республика Татарстан'),
    (17, 'Республика Тыва'),
    (18, 'Удмуртская Республика'),
    (19, 'Республика Хакасия'),
    (21, 'Чувашская Республика'),
    (22, 'Алтайский край'),
    (23, 'Краснодарский край'),
    (24, 'Красноярский край'),
    (25, 'Приморский край'),
    (26, 'Ставропольский край'),
    (27, 'Хабаровский край'),
    (28, 'Амурская область'),
    (29, 'Архангельская область'),
    (30, 'Астраханская область'),
    (31, 'Белгородская область'),
    (32, 'Брянская область'),
    (33, 'Владимирская область'),
    (34, 'Волгоградская область'),
    (33, 'Владимирская область'),
    (34, 'Волгоградская область'),
    (35, 'Вологодская область'),
    (36, 'Воронежская область'),
    (37, 'Ивановская область'),
    (38, 'Иркутская область'),
    (39, 'Калининградская область'),
    (40, 'Калужская область'),
    (41, 'Камчатский край'),
    (42, 'Кемеровская область'),
    (43, 'Кировская область'),
    (44, 'Костромская область'),
    (45, 'Курганская область'),
    (46, 'Курская область'),
    (47, 'Ленинградская область'),
    (48, 'Липецкая область'),
    (49, 'Магаданская область'),
    (50, 'Московская область'),
    (51, 'Мурманская область'),
    (52, 'Нижегородская область'),
    (53, 'Новгородская область'),
    (54, 'Новосибирская область'),
    (55, 'Омская область'),
    (56, 'Оренбургская область'),
    (57, 'Орловская область'),
    (58, 'Пензенская область'),
    (59, 'Пермский край'),
    (60, 'Псковская область'),
    (61, 'Ростовская область'),
    (62, 'Рязанская область'),
    (63, 'Самарская область'),
    (64, 'Саратовская область'),
    (65, 'Сахалинская область'),
    (66, 'Свердловская область'),
    (67, 'Смоленская область'),
    (68, 'Тамбовская область'),
    (69, 'Тверская область'),
    (70, 'Томская область'),
    (71, 'Тульская область'),
    (72, 'Тюменская область'),
    (73, 'Ульяновская область'),
    (74, 'Челябинская область'),
    (75, 'Забайкальский край'),
    (76, 'Ярославская область'),
    (77, 'Город Москва'),
    (78, 'Город Санкт-Петербург'),
    (79, 'Еврейская автономная область'),
    (82, 'Республика Крым'),
    (83, 'Ненецкий автономный округ'),
    (86, 'Ханты-Мансийский автономный округ-Югра'),
    (87, 'Чукотский автономный округ'),
    (89, 'Ямало-Ненецкий автономный округ'),
    (92, 'Город Севастополь'),
    (94, 'Территории за пределами РФ'),
    (95, 'Чеченская Республика')
    )



timezone_dict = {
    'Europe/Kaliningrad': (39, ),
    'Europe/Moscow': (77, 78, 92, 1, 5, 6, 7, 8, 82, 9, 10, 11, 12, 13, 15, 16, 21, 23, 26, 29, 30, 31, 32, 33, 34, 35,
                      36, 37, 40, 43, 44, 46, 47, 48, 50, 51, 52, 53, 57, 58, 60, 61, 62, 64, 67, 68, 69, 71, 73, 76,
                      83, 95),
    'Europe/Samara': (63, 18),
    'Asia/Yekaterinburg': (2, 59, 45, 56, 66, 72, 74, 86, 89),
    'Asia/Omsk': (4, 22, 54, 55, 70),
    'Asia/Krasnoyarsk': (17, 19, 24, 42),
    'Asia/Irkutsk': (3, 38, 75),
    'Asia/Yakutsk': (28, 14),
    'Asia/Vladivostok': (14, 25, 27, 49, 65, 79),
    'Asia/Srednekolymsk': (14, 65),
    'Asia/Kamchatka': (41, 87),
    }

far_east_timezone_dict = {
    'Asia/Yakutsk': ('пгт. Сангар', 'г. Алдан', 'с. Намцы', 'с. Чурапча', 'с. Борогонцы', 'пгт. Хандыга', 'г. Ленск',
                     'с. Майя', 'г. Вилюйск', 'г. Покровск', 'г. Нюрба', 'г. Якутск', 'г. Нерюнгри', 'с. Сунтар',
                     'г. Олёкминск', 'с. Верневилюйск', 'г. Мирный', 'п. Усть-Мая', 'п. Тикси'),
    'Asia/Vladivostok': ('п. Усть-Нера', 'п. Депутатский'),
    'Asia/Srednekolymsk': ('пгт. Зырянка', 'г. Северо-Курильск'),
    }
