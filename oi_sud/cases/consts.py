EVENT_TYPES = (
    (0, 'Передача дела судье'),
    (1, 'Подготовка дела к рассмотрению'),
    (2, 'Рассмотрение дела по существу'),
    (3, 'Обращено к исполнению'),
    (4, 'Вступление постановления (определения) в законную силу'),
    (5, 'Направленная копия постановления (определения) ВРУЧЕНА'),
    (6, 'Вручение копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'),
    (7, 'Материалы дела сданы в отдел судебного делопроизводства'),
    (8, 'Направление копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'),
    (9, 'Протокол (материалы дела) НЕ БЫЛИ возвращены в ТРЕХДНЕВНЫЙ срок'),
    (10,
     'Направленная копия постановления (определения) ВЕРНУЛАСЬ с отметкой о НЕВОЗМОЖНОСТИ ВРУЧЕНИЯ (п. 29.1 Пост. Пленума ВС от 19.12.2013 № 40)'),
    (11, 'Производство по делу возобновлено'),
    (12, 'Регистрация поступившего в суд дела'),
    (13, 'Передача материалов дела судье'),
    (14, 'Дело сдано в отдел судебного делопроизводства'),
    (15, 'Провозглашение приговора'),
    (16, 'Предварительное слушание'),
    (17, 'Решение в отношении поступившего уголовного дела'),
    (18, 'Судебное заседание'),
    (19, 'Сдача материалов дела в архив'),
    (20, 'Изготовлено постановление о назначении административного наказания в полном объеме'),
    (21, 'Изготовлено постановление о прекращении в полном объеме'),
    (22, 'Окончено производство по исполнению'),
    (23, 'Дело оформлено'),
    (24, 'Дело передано в архив'),
    (25, 'Материалы переданы в производство судье'),
    (26, 'Истребованы материалы'),
    (27, 'Оставлено без рассмотрения'),
    (28, 'Поступили истребованные материалы'),
    (29, 'Направление копии решения (определения) в соотв. с чч. 2, 2.1, 2.2 ст. 30.8 КоАП РФ'),
    (30, 'Направленная копия решения (определения) ВРУЧЕНА'),
    (31, 'Вступило в законную силу'),
    (32, 'Оставлено без рассмотрения в связи с пропуском срока обжалования'),
    (33,
     'Направленная копия решения (определения) ВЕРНУЛАСЬ с отметкой о НЕВОЗМОЖНОСТИ ВРУЧЕНИЯ (п. 29.1 Пост. Пленума ВС от 19.12.2013 № 40)'),
    (34, 'Вынесено постановление о назначении судебного заседания'),
    (35, 'Снято с апелляционного рассмотрения'),
    (36, 'Дело отправлено мировому судье'),
    (37, 'Отзыв жалобы (представления)'),
    (38, 'Вручение копии решения (определения) в соотв. с чч. 2, 2.1, 2.2 ст. 30.8 КоАП РФ'),
    (39, 'Дело передано в экспедицию'),
    (40, 'Протокол (материалы дела) БЫЛИ возвращены в ТРЕХДНЕВНЫЙ срок'),
    (41, 'Продление срока рассмотрения'),

)

EVENT_RESULT_TYPES = (
    (0, 'Назначено предварительное слушание'),
    (1, 'Назначено судебное заседание'),
    (2, 'Рассмотрение отложено'),
    (3, 'Заседание отложено'),
    (4, 'Протокол об административном правонарушении (материалы дела) возвращен(ы)  (в пор. ст.29.4 п.4)'),
    (5, 'Дело возвращено прокурору'),
    (6, 'Возвращено без рассмотрения'),
    (7, 'Производство по делу прекращено'),
    (8, 'Производство по делу приостановлено'),
    (9, 'Производство прекращено'),
    (10, 'Вынесено постановление о назначении административного наказания'),
    (11, 'Вынесено постановление в порядке гл. 51 УПК (о применении ПМ медицинского характера)'),
    (12, 'Постановление приговора'),
    (13, 'Провозглашение приговора окончено'),
    (14,
     'Оглашение резолютивной части постановления о назначении административного наказания (изготовление постановления в полном объеме отложено)'),
    (15, 'Передано по подведомственности'),
    (16,
     'Оглашение резолютивной части постановления о прекращении производства (изготовление постановления в полном объеме отложено)'),
    (17, 'Объявлен перерыв'),
    (18, 'Оставлено без изменения'),
    (19, 'Отменено с возвращением на новое рассмотрение'),
    (20, 'Отменено с прекращением производства'),
    (21, 'Оставлено без рассмотрения'),
    (22, 'Оставлено без рассмотрения в связи с пропуском срока обжалования'),
    (23, 'Производство по жалобе прекращено'),
    (24, 'Изменено'),
    (25, 'Дело рассмотрено по существу'),
    (26, 'Апелляционное производство прекращено'),
)

RESULT_TYPES = (
    (0, 'Апелляционное ПРОИЗВОДСТВО ПРЕКРАЩЕНО'),
    (1, 'ВОЗВРАЩЕНО ПРОКУРОРУ'),
    (2, 'Вынесен ПРИГОВОР'),
    (3, 'Вынесено другое ПОСТАНОВЛЕНИЕ'),
    (4, 'Направлено ПО ПОДСУДНОСТИ (подведомственности)'),
    (5, 'ОСТАВЛЕНО БЕЗ РАССМОТРЕНИЯ в связи с неявкой сторон'),
    (6, 'Представление (жалоба) ОТОЗВАНЫ'),
    (7, 'Применены ПРИНУДИТЕЛЬНЫЕ МЕРЫ МЕДИЦИНСКОГО ХАРАКТЕРА'),
    (8, 'СНЯТО с апелляционного рассмотрения'),
    (9, 'Уголовное дело ПРЕКРАЩЕНО'),
    (10, 'Отмена'),
    (11,
     'Вынесено определение о возвращении протокола об АП и др. материалов дела в орган, долж. лицу ... в случае составления протокола и оформления других материалов дела неправомочными лицами, ...'),
    (12, 'Вынесено определение о передаче дела по подведомственности (ст 29.9 ч.2 п.2 и ст 29.4 ч.1 п.5)'),
    (13, 'Вынесено постановление о назначении административного наказания'),
    (14, 'Вынесено постановление о прекращении производства по делу об адм. правонарушении'),
    (15, 'Оставлено без изменения'),
    (16, 'Отменено с прекращением производства'),
    (17, 'Оставлено без рассмотрения'),
    (18, 'Отменено с возвращением на новое рассмотрение'),
    (19, 'Оставлено без рассмотрения в связи с пропуском срока обжалования'),
    (20, 'Производство по жалобе прекращено'),
    (21, 'Изменено'),
)

APPEAL_RESULT_TYPES = (
    (1, 'Отмена'),
    (2, 'Жалоба (протест) на определение (постановление) не по существу дела - рассмотрена'),
    (3, 'Изменено'),
    (4, 'Направлено по подведомственности'),
    (5, 'Оставлено без изменения'),
    (6, 'Оставлено без рассмотрения'),
    (7, 'Оставлено без рассмотрения в связи с пропуском срока обжалования'),
    (8, 'Отменено с возвращением на новое рассмотрение'),
    (9, 'Отменено с направлением по подведомственности'),
    (10,'Отменено с прекращением производства'),
    (11,'Производство по жалобе прекращено'),
    (12,'вынесено иное определение не по существу дела'),
    (13,'Без изменения'),
    (14,'Отменено с возвращением дела на новое рассмотрение'),
    (15,'Отменено с прекращением производства по делу'),
    (16,'Оставлено без рассмотрения или возвращено'),
    (17,'производство прекращено'),
    (18,'Отменено'),


)

adm_type_one_params_string = '/modules.php?name=sud_delo&srv_num=1&name_op=r&delo_id=DELOID&case_type=CASETYPE&new=0&delo_table=DELOTABLE&nc=1'

adm2_type_one_params_string = '/modules.php?name=sud_delo&srv_num=1&name_op=r&delo_id=DELOID&case_type=CASETYPE&new=0&delo_table=DELOTABLE&nc=1'

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

adm_type_two_params_string = '/modules.php?name_op=r&nc=1&name=sud_delo&srv_num=1&_deloId=DELOID&case__vnkod=XXX&process-type=DELOID_CASETYPE_0'

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

cr_type_one_params_string = '/modules.php?name=sud_delo&srv_num=1&name_op=r&delo_id=DELOID&case_type=CASETYPE&new=0&delo_table=DELOTABLE&nc=1'

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

cr_type_two_params_string = '/modules.php?name_op=r&name=sud_delo&srv_num=1&_deloId=DELOID&case__case_type=CASETYPE&_new=0&case__vnkod=XXX&case__num_build=1&case__case_numberss=&part__namess=&process-type=DELOID_CASETYPE_0&case__ss='

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

site_type_dict = {
    '1': {'koap': {'string': adm_type_one_params_string, 'params_dict': adm_type_one_params_dict},
          'uk': {'string': cr_type_one_params_string, 'params_dict': cr_type_one_params_dict}},
    '2': {'koap': {'string': adm_type_two_params_string, 'params_dict': adm_type_two_params_dict},
          'uk': {'string': cr_type_two_params_string, 'params_dict': cr_type_two_params_dict}},
}

site_types_by_codex = {'koap': {'1': {'string': adm_type_one_params_string, 'params_dict': adm_type_one_params_dict},
                                '2': {'string': adm_type_two_params_string, 'params_dict': adm_type_two_params_dict}},
                       'uk': {'1': {'string': cr_type_one_params_string, 'params_dict': cr_type_one_params_dict},
                              '2': {'string': cr_type_two_params_string, 'params_dict': cr_type_two_params_dict}}}

instances_dict = {'koap': {'1': ('1500001', '0', 'adm_case'), '2': ('1502001', '0', 'adm1_case')},
                  'uk': {'1': ('1540006', '0', 'u1_case'), '2': ('1540006', '50780001', 'u1_case')}}
