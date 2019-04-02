import datetime
import json
import re
import re
import requests
import time
from bs4 import BeautifulSoup
from requests import Request, Session
from urllib.parse import urlparse
from user_agent import generate_user_agent, generate_navigator

from oi_sud.core.consts import *


class CommonParser(object):

    @staticmethod
    def send_get_request(url, encoding='', gen_useragent=False, has_encoding=False, content_text_status=False):
        """accessory function for sending requests"""
        s = Session()
        req = Request('GET', url)
        prepped = req.prepare()
        if gen_useragent:
            prepped.headers['User-Agent'] = generate_user_agent()
        r = s.send(prepped)
        # return r.status_code
        if encoding:
            r.encoding = encoding
        if content_text_status:
            return r.content, r.text, r.status_code
        if has_encoding:
            return r.content
        else:
            return r.text

    @staticmethod
    def generate_url(court_url, string, params_dict, params):
        result_string = ''
        result_string += court_url
        result_string += string
        for k, v in params.items():
            if k in params_dict:
                result_string += '&{0}={1}'.format(params_dict[k], v)
        return result_string

    @staticmethod
    def generate_url_first(court_url, case_type, params):
        if case_type == 'administrative':
            print(generate_url(court_url, adm_type_one_params_string, adm_type_one_params_dict, params))
            return generate_url(court_url, adm_type_one_params_string, adm_type_one_params_dict, params)
        elif case_type == 'criminal':
            return generate_url(court_url, cr_type_one_params_string, cr_type_one_params_dict, params)

    @staticmethod
    def generate_url_second(court_url, case_type, params):
        if case_type == 'administrative':
            return generate_url(court_url, adm_type_two_params_string, adm_type_two_params_dict, params)
        elif case_type == 'criminal':
            return generate_url(court_url, cr_type_two_params_string, cr_type_two_params_dict, params)
