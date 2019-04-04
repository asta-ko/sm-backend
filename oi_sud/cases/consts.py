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

site_type_dict = {
    '1': {'koap': {'string': adm_type_one_params_string, 'params_dict': adm_type_one_params_dict},
          'uk': {'string': cr_type_one_params_string, 'params_dict': cr_type_one_params_dict}},
    '2':{'koap': {'string': adm_type_two_params_string, 'params_dict': adm_type_two_params_dict},
          'uk': {'string': cr_type_two_params_string, 'params_dict': cr_type_two_params_dict}},
}

site_types_by_codex = {'koap': {'1': {'string': adm_type_one_params_string, 'params_dict': adm_type_one_params_dict},
                           '2': {'string': adm_type_two_params_string, 'params_dict': adm_type_two_params_dict}},
                  'uk': {'1': {'string': cr_type_one_params_string, 'params_dict': cr_type_one_params_dict},
                         '2': {'string': cr_type_two_params_string, 'params_dict': cr_type_two_params_dict}}}