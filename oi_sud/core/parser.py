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