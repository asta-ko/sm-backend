adm_type_one_params_string = '/modules.php?name=sud_delo&srv_num=1&name_op=r&delo_id=1500001&case_type=0&new=0&delo_table=adm_case'

adm_type_one_params_dict = {'last_name': 'adm_parts__NAMES',
                            'case_number': 'adm_case__CASE_NUMBERSS',
                            'case_uid': 'adm_case__JUDICIAL_UIDSS',
                            'protocol_number': 'adm_case__PR_NUMBERSS',
                            'entry_date_from': 'adm_case__ENTRY_DATE1D',
                            'entry_date_to': 'adm_case__ENTRY_DATE2D',
                            'judge': 'ADM_CASE__JUDGE',
                            'result_date_from': 'adm_case__RESULT_DATE1D',
                            'result_date_to': 'adm_case__RESULT_DATE2D',
                            'case_result': 'ADM_CASE__RESULT',
                            'articles': 'adm_parts__LAW_ARTICLESS',
                            'publish_date_from': 'adm_document__PUBL_DATE1D',
                            'publish_date_to': 'adm_document__PUBL_DATE2D',
                            'validity_date_from': 'ADM_CASE__VALIDITY_DATE1D',
                            'validity_date_to': 'ADM_CASE__VALIDITY_DATE2D'
                            }

adm_type_two_params_string = '/modules.php?name_op=r&name=sud_delo&srv_num=1&_deloId=1500001&case__case_type=0&_new=0&case__num_build=1&process-type=1500001_0_0'

adm_type_two_params_dict = {'last_name': 'part__namess',
                            'case_number': 'case__case_numberss',
                            'case_uid': 'case__judicial_uidss',
                            'protocol_number': 'case__pr_numberss',
                            'entry_date_from': 'case__entry_date1d',
                            'entry_date_to': 'case__entry_date2d',
                            'judge': 'case__judge',
                            'result_date_from': 'case__result_date1d',
                            'result_date_to': 'case__result_date2d',
                            'case_result': 'case__result',
                            'articles': 'parts__law_articless',
                            'publish_date_from': 'document__publ_date1d',
                            'publish_date_to': 'document__publ_date2d',
                            'validity_date_from': 'case__validity_date1d',
                            'validity_date_to': 'case__validity_date2d'
                            }

cr_type_one_params_string = '/modules.php?name=sud_delo&srv_num=1&name_op=r&delo_id=1540006&case_type=0&new=0&delo_table=u1_case'

cr_type_one_params_dict = {'last_name': 'U1_DEFENDANT__NAMESS',
                           'case_number': 'U1_CASE__CASE_NUMBERSS',
                           'case_uid': 'U1_CASE__JUDICIAL_UIDSS',
                           'entry_date_from': 'U1_CASE__ENTRY_DATE1D',
                           'entry_date_to': 'U1_CASE__ENTRY_DATE2D',
                           'judge': 'U1_CASE__JUDGE',
                           'result_date_from': 'U1_CASE__RESULT_DATE1D',
                           'result_date_to': 'U1_CASE__RESULT_DATE2D',
                           'case_result': 'U1_CASE__RESULT',
                           'articles': 'U1_DEFENDANT__LAW_ARTICLESS',
                           'publish_date_from': 'U1_DOCUMENT__PUBL_DATE1D',
                           'publish_date_to': 'U1_DOCUMENT__PUBL_DATE2D',
                           'validity_date_from': 'U1_CASE__VALIDITY_DATE1D',
                           'validity_date_to': 'U1_CASE__VALIDITY_DATE2D'
                           }

cr_type_two_params_string = '/modules.php?name_op=r&name=sud_delo&srv_num=1&_deloId=1540006&case__case_type=0&_new=0&process-type=1540006_0_0&case__vnkod=XXX'

cr_type_two_params_dict = {'last_name': 'parts__namess',
                           'case_number': 'case__case_numberss',
                           'case_uid': 'case__judicial_uidss',
                           'entry_date_from': 'case__entry_date1d',
                           'entry_date_to': 'case__entry_date2d',
                           'judge': 'case__judge',
                           'result_date_from': 'case__result1d',
                           'result_date_to': 'case__result1d',
                           'case_result': 'case__result',
                           'articles': 'parts__law_articless',
                           'publish_date_from': 'document__publ_date1d',
                           'publish_date_to': 'document__publ_date2d',
                           'validity_date_from': 'case__validity_date1d',
                           'validity_date_to': 'case__validity_date2d'
                           }

region_choices = (
(0, 'Чеченская Республика'), (1, 'Мурманская область'), (2, 'Кемеровская область'), (3, 'Кировская область'),
(4, 'Тверская область'), (5, 'Забайкальский край'), (6, 'Ленинградская область'), (7, 'Рязанская область'),
(8, 'Удмуртская Республика'), (9, 'Республика Саха (Якутия)'), (10, 'Волгоградская область'),
(11, 'Ростовская область'), (12, 'Московская область'), (13, 'Амурская область'), (14, 'Чувашская Республика '),
(15, 'Воронежская область'), (16, 'Республика Адыгея'), (17, 'Свердловская область'), (18, 'Нижегородская область'),
(19, 'Сахалинская область'), (20, 'Псковская область'), (21, 'Калининградская область'), (22, 'Новгородская область'),
(23, 'Костромская область'), (24, 'Тульская область'), (25, 'Брянская область'), (26, 'Республика Башкортостан'),
(27, 'Курская область'), (28, 'Республика Дагестан'), (29, 'Приморский край'), (30, 'Курганская область'),
(31, 'Город Москва'), (32, 'Иркутская область'), (33, 'Пензенская область'), (34, 'Ярославская область'),
(35, 'Республика Коми'), (36, 'Алтайский край'), (37, 'Ставропольский край'), (38, 'Ульяновская область'),
(39, 'Новосибирская область'), (40, 'Саратовская область'), (41, 'Белгородская область'),
(42, 'Ямало-Ненецкий автономный округ'), (43, 'Магаданская область'), (44, 'Камчатский край'),
(45, 'Тюменская область'), (46, 'Республика Северная Осетия-Алания'), (47, 'Республика Тыва'),
(48, 'Ханты-Мансийский автономный округ-Югра'), (49, 'Республика Татарстан '), (50, 'Краснодарский край'),
(51, 'Красноярский край'), (52, 'Вологодская область'), (53, 'Республика Мордовия'), (54, 'Томская область'),
(55, 'Самарская область'), (56, 'Оренбургская область'), (57, 'Кабардино-Балкарская Республика'),
(58, 'Республика Крым'), (59, 'Челябинская область'), (60, 'Тамбовская область'), (61, 'Республика Ингушетия'),
(62, 'Пермский край'), (63, 'Орловская область'), (64, 'Омская область'), (65, 'Республика Карелия'),
(66, 'Астраханская область'), (67, 'Архангельская область'), (68, 'Чукотский автономный округ'),
(69, 'Республика Бурятия'), (70, 'Владимирская область'), (71, 'Калужская область'), (72, 'Смоленская область'),
(73, 'Республика Алтай'), (74, 'Липецкая область'), (75, 'Ивановская область'), (76, 'Республика Хакасия'),
(77, 'Республика Марий Эл'), (78, 'Город Севастополь'), (79, 'Хабаровский край'), (80, 'Еврейская автономная область'),
(81, 'Город Санкт-Петербург'), (82, 'Республика Калмыкия'), (83, 'Карачаево-Черкесская Республика'),
(84, 'Территории за пределами РФ'), (85, 'Ненецкий автономный округ '))
