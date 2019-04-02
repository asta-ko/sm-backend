# -*- coding: utf-8 -*-
import json
import re
from airtable import airtable
from airtable.airtable import Airtable
from bs4 import BeautifulSoup

from oi_sud.core.consts import region_choices
from oi_sud.core.parser import CommonParser
from .models import Court, Judge


class CourtsParser(CommonParser):
    at_table = 'Суды общей юрисдикции'
    airtable_app = 'appYdzQXoOfxI1xvV'
    airtable_key = 'keywzBJ8QNsoO4RlZ'

    def get_site_type(self, url):
        if 'mos-gorsud' in url:
            return 3
        url = url + '/modules.php?name=sud_delo&srv_num=1'
        txt = self.send_get_request(url)
        result_two = re.search(r'Список дел, назначенных к слушанию на', txt)
        result_one = re.search(r'Вывести список дел, назначенных на дату', txt)
        if result_one:
            return 1
        elif result_two:
            return 2
        return 1

    def get_vnkod(self, url):
        url = url + '/modules.php?name=sud_delo&srv_num=1&name_op=sf'
        txt = self.send_get_request(url)
        page = BeautifulSoup(txt, 'html.parser')
        inp = page.find(name='input', attrs={"name": "case__vnkod"})
        return inp['value']

    def get_courts_table(self, limit=None):
        at = Airtable(self.airtable_app, self.airtable_key)
        offset = ''
        records = []

        while True:
            table = at.get(self.at_table, offset=offset)
            records += table["records"]
            if "offset" in table:
                offset = table["offset"]
            else:
                break
        # print(records)
        if limit is not None:
            return records[:limit]
        else:
            return records

    def get_regions(self):
        regions = []
        records = self.get_courts_table()
        for rec in records:
            # print(rec)
            region = rec['fields']['регион']
            if region not in regions:
                regions.append(region)
        r = []
        for count, item in enumerate(regions):
            r.append((count, item))
        print(tuple(r))

    def parse_judges_type_one(self, court):
        judges = []
        for x in ['U1_CASE', 'adm_case']:
            url = f'{court.url}/modules.php?name=sud_delo&name_op=cat&nc=1&curent_delo_table={x}&fieldname=JUDGE'
            txt = self.send_get_request(url)
            page = BeautifulSoup(txt, 'html.parser')
            divs = page.findAll('div', {"onmouseout": "button_out(this);"})
            judges += [x.text.strip() for x in divs if x.text.strip() != '']
        judges = list(set(judges))
        return judges

    def parse_judges_type_two(self, court):
        judges = []
        court_url = court.url
        for x in ['1540006', '1500001']:
            url = f'{court_url}/modules.php?name=sud_delo&name_op=cat&nc=1&_deloId=1540006&_caseType=0&_new=0&_table=case&_fieldname=judge&srv_num=1'
            txt = self.send_get_request(url)
            page = BeautifulSoup(txt, 'html.parser')
            div = page.findAll('div', id='search_results')[0]
            judges += json.loads(div.text).values()
        judges = list(set(judges))
        return judges

    def get_and_save_judges(self, court):
        judges = []
        if court.site_type == 1:
            judges = self.parse_judges_type_one(court)
        elif court.site_type == 2:
            judges = self.parse_judges_type_two(court)
        for name in judges:
            if not Judge.objects.filter(name=name, court=court).exists():
                j = Judge.objects.create(name=name, court=court)
                print(j)

    def save_all_judges(self):
        errors = []
        for court in Court.objects.all():
            print(court.url)
            try:
                self.get_and_save_judges(court)
            except Exception as e:
                print('error', e, court.url)
                errors.append(court.url)
        print('Success')
        print(errors)

    def parse_table_record(self, rec):

        region_dict = dict((y, x) for x, y in region_choices)

        court_dict = {}

        court_dict['title'] = rec['fields']['название суда'].replace('  ', ' ')

        if 'Верховный' in court_dict['title'] or 'Постоянное' in court_dict['title'] or ('Москва' in court_dict[
            'title'] and self.at_table != 'Суды Москвы'):
            return

        court_dict['type'] = self.get_court_type(court_dict['title'])[0]

        court_dict['instance'] = self.get_court_type(court_dict['title'])[1]

        if rec['fields'].get('url'):
            court_dict['url'] = rec['fields']['url'].replace('sudrf.ru/', 'sudrf.ru')

        court_dict['site_type'] = self.get_site_type(court_dict['url'])

        if rec['fields'].get('регион') and region_dict.get(rec['fields']['регион']) is not None:
            court_dict['region'] = region_dict[rec['fields']['регион']]

        if rec['fields'].get('адрес'):
            court_dict['full_address'] = rec['fields']['адрес']

        if rec['fields'].get('телефон'):
            phones = rec['fields'].get('телефон')
            phone_code = phones.split(')')[0] + ')'
            phones = phones.replace(phone_code + ' ', '').replace(phone_code, '').replace(') ', '), ')
            court_dict['phone_numbers'] = [f'{phone_code}{x}'[:25] for x in phones.split(', ')]
        else:
            court_dict['phone_numbers'] = []

        if rec['fields'].get('email'):
            court_dict['email'] = rec['fields']['email'].split(' ')[0]

        return court_dict

    def save_courts(self, limit=None):

        records = self.get_courts_table(limit)
        count = 0
        errors = []

        for rec in records:

            try:
                court_dict = self.parse_table_record(rec)
                court = self.save_court(court_dict)
                if court:
                    count += 1
                print(court)
            except Exception as e:
                error = str(e)
                errors.append(error)

        print(f'{count} courts saved')
        print('errors: ', errors)

    def save_court(self, court_dict):
        if Court.objects.filter(title=court_dict['title']).exists():
            return

        court = Court.objects.create(**court_dict)
        if court.site_type == 2:
            court.vn_kod = self.get_vnkod(court.url)
            court.save()
        return court

    @staticmethod
    def get_court_type(court_title):
        court_title = court_title.lower()
        if 'район' in court_title:
            return 0, 1
        elif 'городской' in court_title and (
                'санкт-петербург' in court_title or 'севастополь' in court_title or 'москв' in court_title):
            return 2, 2
        elif 'городской' in court_title:
            return 1, 1
        elif 'областной' in court_title:
            return 3, 2
        elif 'краевой' in court_title:
            return 4, 2
        elif 'автономного округа' in court_title or 'автономной области' in court_title:
            return 7, 2
        elif 'гарнизонный военный' in court_title:
            return 5, 1
        elif 'окружной военный' in court_title or ' флотский' in court_title:
            return 6, 2


courts_parser = CourtsParser()


class MoscowCourtParser(CourtsParser):
    at_table = 'Суды Москвы'
    airtable_app = 'appYdzQXoOfxI1xvV'
    airtable_key = 'keywzBJ8QNsoO4RlZ'

    def get_phone(self):
        records = self.get_courts_table()
        for rec in records:
            url = rec['fields'].get('url')
            if not url:
                continue
            txt = self.send_get_request(url)
            page = BeautifulSoup(txt, 'html.parser')
            phone = page.select('div.icon_phone')[0].find('div').text
            print(rec['fields'].get('название суда'), phone)

    def save_all_judges(self):
        errors = []
        for court in Court.objects.filter(site_type=3):
            print(court.url)
            try:
                self.get_and_save_judges(court)
            except Exception as e:
                print('error', e, court.url)
                errors.append(court.url)
        print('Success')
        print(errors)

    def get_and_save_judges(self, court):
        raise NotImplementedError


moscow_courts_parser = MoscowCourtParser()
