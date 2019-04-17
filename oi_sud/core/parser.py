import datetime
import json
import requests
from requests import Request, Session
from requests.packages.urllib3.util.retry import Retry
from urllib.parse import urlparse
from user_agent import generate_user_agent, generate_navigator

from oi_sud.core.consts import *


class CommonParser(object):

    @staticmethod
    def send_get_request(url, gen_useragent=False):
        """accessory function for sending requests"""

        retries = Retry(total=4,
                        backoff_factor=0.2,
                        method_whitelist=frozenset(['GET']),
                        status_forcelist=[500, 502, 503, 504, 204])

        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        session = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=retries)
        session.mount('https://', a)

        req = Request('GET', url)
        prepped = req.prepare()

        if gen_useragent:
            prepped.headers['User-Agent'] = generate_user_agent()

        r = session.send(prepped)

        return r.text, r.status_code
