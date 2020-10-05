import logging
import re

import requests
from requests import Request
from requests.packages.urllib3.util.retry import Retry
from requests_futures.sessions import FuturesSession
from user_agent import generate_user_agent

logging.getLogger("urllib3").setLevel(logging.WARNING)


class CommonParser(object):
    proxies = ['http://ukX6gkiRKT:GaFrw2uNRJ@45.140.63.231:54745',
               'http://ukX6gkiRKT:GaFrw2uNRJ@45.159.84.105:58246',
               'http://ukX6gkiRKT:GaFrw2uNRJ@91.220.229.180:50371',
               'http://ukX6gkiRKT:GaFrw2uNRJ@194.156.93.112:48002',
               'http://ukX6gkiRKT:GaFrw2uNRJ@176.103.95.52:64521']

    retries = Retry(total=4,
                    backoff_factor=0.2,
                    method_whitelist=frozenset(['GET']),
                    status_forcelist=[500, 502, 503, 504, 204])

    def send_get_requests(self, urls, callback=None):
        with FuturesSession(max_workers=5) as session:
            user_agent = generate_user_agent()
            session.headers.update({'User-Agent': user_agent})
            a = requests.adapters.HTTPAdapter(max_retries=self.retries)
            session.mount('https://', a)
            session.mount('http://', a)
            rs = (session.get(u, hooks={
                'response': callback
            }) for u in urls)
            for r in rs:
                r.result()

    def send_get_request(self, url, gen_useragent=True, extended=False):
        """accessory function for sending requests"""
        import urllib3
        import random
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        session = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=self.retries)
        session.mount('https://', a)

        proxy_index = random.randint(0, len(self.proxies) - 1)
        session.proxies = {"http": self.proxies[proxy_index], "https": self.proxies[proxy_index]}

        req = Request('GET', url)
        prepped = req.prepare()

        if gen_useragent:
            prepped.headers['User-Agent'] = generate_user_agent()

        r = session.send(prepped, verify=False)
        if extended:

            try:
                pattern = re.compile(r"filename\*?=.*\.([a-z0-9]+)")
                txt = r.headers['Content-Disposition']
                exten = pattern.search(txt, re.UNICODE).group(1)
            except Exception:
                txt = ''
                exten = ''

            return r, r.status_code, r.content, exten

        return r.text, r.status_code
