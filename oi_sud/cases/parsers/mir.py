# coding: utf-8

# In[ ]:


# coding=utf-8
import re

from bs4 import BeautifulSoup
from dateparser.conf import settings as dateparse_settings
from django.utils.timezone import get_current_timezone
from oi_sud.cases.consts import msudrf_params_dict
from oi_sud.cases.parsers.main import CourtSiteParser
from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.courts.models import Court

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False


class MsudrfParser(CourtSiteParser):

    def get_pages_number(self, page):
        # получаем число страниц с делами (скорее всего больше одной будет редко, но делать нужно)
        paging = page.find('ul', class_='paging')
        if paging:
            key = int(paging.findAll('li')[-1].a.text.strip())
            return key
        else:
            return 1

    def get_cases_urls_from_list(self, page):
        # получаем урлы карточек дел из страницы поиска
        urls = [x.a['href'] for x in page.findAll('td', class_='lawcase-number-td')[1:]]
        # print('.', end='')
        return urls

    def get_all_cases_urls(self, limit_pages=False):
        # Получаем все урлы дел по данной статье
        urls = []
        for i in range(get_pages_number(search)):
            url_search = url.replace('&pageNum_Recordset1=0', '') + '&pageNum_Recordset1=' + str(i)
            txt, status_code = self.send_get_request(url_search)
            if status_code != 200:
                print("GET error: ", status_code)
            else:
                page = BeautifulSoup(txt, 'html.parser')
                urls.extend(get_cases_urls_from_list(page))
        return urls

    def get_raw_case_information(self, url):

        case_info = {}

        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            print("GET error: ", status_code)
            return

        data = BeautifulSoup(txt, 'html.parser')

        case_info['url'] = url

        pages = data.findAll('table', class_="tablcont")
        search_data = self.get_search_data(url)
        main_data = self.get_main_data(pages)

        case_info['events'] = self.get_events_data(pages)
        case_info['defenses'] = self.get_defenses_data(pages)

        case_info['case_number'] = search_data['case_number']
        case_info['entry_date'] = search_data['entry_date']
        case_info['protocol_number'] = main_data['protocol_number']
        case_info['judge'] = search_data['judge']
        case_info['result_date'] = search_data['result_date']
        case_info['result_type'] = search_data['result_type']
        search_data['result_text_url'] = search_data['result_text_url']

        if search_data['result_text_url'] != '':
            case_info['result_text'] = self.get_result_text(search_data['result_text_url'])
            match = re.search('УИД (.*)', case_info['result_text'])
            if match:
                case_info['case_uid'] = match.group(1)
            else:
                case_info['case_uid'] = ''
        else:
            case_info['result_text'] = ''
            case_info['case_uid'] = ''

        return case_info

    def get_result_text(self, url):
        # получаем текст решения
        txt, status_code = self.send_get_request(url)

        if status_code != 200:
            print("GET error: ", status_code)
            return

        data = BeautifulSoup(txt, 'html.parser')

        result_text = data.find('div', class_='lawcase-document').text.strip()
        return result_text

    def get_search_data(self, url):

        result_dict = {
            'case_number': '',
            'entry_date': '',
            'info': '',
            'judge': '',
            'result_date': '',
            'result_type': '',
            'result_text_url': ''
        }

        keys = {
            'Номер дела': 'case_number', '№ дела': 'case_number',
            'Дата поступления': 'entry_date',
            'Информация по делу': 'info', 'Правонарушение': 'info',
            'Судья': 'judge',
            'Дата решения': 'result_date',
            'Решение': 'result_type',
            'Судебныеакты': 'result_text_url'
        }

        txt, status_code = self.send_get_request(url)

        if status_code != 200:
            print("GET error: ", status_code)
            return

        data = BeautifulSoup(txt, 'html.parser')

        match = re.search('ДЕЛО № (.*)', data.text)
        if match:
            case_number = match.group(1)

        delo_id = ''

        match_delo = re.search('delo_id=([^&]*)', url)
        if match_delo:
            delo_id = match_delo.group(1)

            if delo_id == '1500001':
                search_url = url.split('?')[
                                 0] + '?' + 'name=sud_delo&delo_id=1500001&op=sf&adm_case__CASE_NUMBERSS=' + case_number
            elif delo_id == '1540006':
                search_url = url.split('?')[
                                 0] + '?' + 'name=sud_delo&delo_id=1540006&op=sf&u1_case__CASE_NUMBERSS=' + case_number
            else:
                return result_dict

        if search_url:

            txt, status_code = self.send_get_request(search_url)

            if status_code != 200:
                print("GET error: ", status_code)
                return

            page = BeautifulSoup(txt, 'html.parser')

            original_dict = {}

            if page.find('table', {"id": "tablcont"}) is not None:
                table = page.find('table', {"id": "tablcont"})
                headers = [x.text.strip() for x in table.find('tr').findAll('th')]
                if len(headers) == 0:
                    headers = [x.text.strip() for x in table.thead.findAll('td')]
                    tds = [x.a["href"] if x.text.strip() == "" and x.a != None else x.text.strip() for x in
                           table.tbody.findAll('td')]
                else:
                    tds = [x.a["href"] if x.text.strip() == "" and x.a != None else x.text.strip() for x in
                           table.findAll('tr')[1].findAll('td')]
                original_dict = dict(zip(headers, tds))

            for key in keys.keys():
                if key in original_dict.keys():
                    if keys[key] == 'result_text_url' and original_dict[key] != '':
                        result_dict[keys[key]] = url.split('/modules')[0] + original_dict[key]
                    else:
                        result_dict[keys[key]] = original_dict[key]

        return result_dict

    def get_main_data(self, pages):
        result_dict = {
            'protocol_number': '',
            'judge': ''
        }

        keys = {
            'Номер протокола об АП': 'protocol_number',
            'Передано в производство судье': 'judge', 'Дело находится в производстве судьи': 'judge',
            'Результат рассмотрения (подготовки к рассмотрению) дела': 'result_type',
            'Результат рассмотрения по делу': 'result_type',
            'Дата вынесения постановления (определения) по делу': 'result_date', 'Дата рассмотрения дела': 'result_date'
        }

        if (len(pages) > 0):
            page = pages[0]

            rows = [x for x in page.findAll('tr')]

            original_dict = {x[0]: x[1] for x in [[y.text.strip() for y in row.findAll('td')] for row in rows] if
                             len(x) > 1}

            for key in keys.keys():
                if key in original_dict.keys():
                    result_dict[keys[key]] = original_dict[key]

        return result_dict

    def get_events_data(self, pages):
        result_dict = [{'type': ''
                           , 'date': ''
                           , 'time': ''
                           , 'courtroom': ''
                           , 'result': ''}]

        keys = {
            'Наименование события': 'type',
            'Дата события': 'date',
            'Время события': 'time',
            'Результат события': 'result', 'Результат': 'result',
            'Судья': 'judge'
        }

        if len(pages) > 1:

            page = pages[1]

            thead = page.thead
            if thead is None:
                headers = [x.text for x in page.findAll('b')]
                cells = [x.text.strip() for x in page.select("td")[len(headers) + 1:]]
                tds = []
                for i in range(int(len(cells) / len(headers))):
                    td = cells[len(headers) * i: len(headers) * (i + 1)]
                    tds.append(td)
            else:
                headers = [x.text for x in thead.findAll('td')]
                tds = [[y.text for y in x] for x in page.select("tr")[1:]]

            original_dict = [dict(zip(headers, x)) for x in tds]

            result_dict = []

            for i in range(len(original_dict)):
                pre_result_dict = {'type': '',
                                   'date': '',
                                   'time': '',
                                   'courtroom': '',
                                   'result': ''}
                for key in keys.keys():
                    if key in original_dict[i].keys():
                        if keys[key] == 'judge':
                            pre_result_dict[keys[key]] = original_dict[i][key].replace('Решение принял: ', '')
                        else:
                            pre_result_dict[keys[key]] = original_dict[i][key]
                result_dict.append(pre_result_dict)
        return result_dict

    def get_defenses_data(self, pages):
        result_dict = [{'defendant': '', 'codex_articles': ''}]

        keys = {
            'Сторона по делу (ФИО, наименование)': 'defendant', 'ФИО': 'defendant',
            'ФИО подсудимого': 'defendant',
            'Вид участника производства': 'type', 'Процессуальный статус лица, участвующего в деле': 'type',
            'Главная статья (КоАП, ТК ...)': 'codex_articles', 'Список статей кодекса (КоАП, ТК ...)': 'codex_articles',
            'Перечень всех статей (по обвинению)': 'codex_articles', 'Основная статья (по обвинению)': 'codex_articles',
            'Наименование вида правонарушения': 'info',
            'Дата вынесения приговора (опр., пост.)': 'result_date',
            'Приговор (опр., пост.)': 'result'
        }

        if (len(pages) > 2):

            page = pages[2]

            thead = page.thead

            if thead is None:
                d = [[y.text.strip() for y in x.findAll('td')] for x in page.findAll('tr') if len(x) > 1]
                headers = [x[0] for x in d]
                tds = [x[1] for x in d]
                original_dict = [dict(d)]
            else:
                headers = [x.text.strip() for x in page.thead.findAll('td')]
                tds = [[y.text.strip() for y in x] for x in page.select("tr")[1:] if len(x) > 1]
                original_dict = [dict(zip(headers, x)) for x in tds]

            result_dict = []

            for i in range(len(original_dict)):
                pre_result_dict = {'defendant': '', 'codex_articles': ''}
                for key in keys.keys():
                    if key in original_dict[i].keys():
                        pre_result_dict[keys[key]] = original_dict[i][key]
                result_dict.append(pre_result_dict)

        return result_dict

    def get_koap_article(self, raw_string):
        # получаем объекты статей КОАП из строки, полученной из карточки дела
        raise NotImplementedError

    def get_uk_articles(self, raw_string):
        # получаем объекты статей УК из строки, полученной из карточки дела
        raise NotImplementedError


class MsudrfCasesGetter(CommonParser):

    @staticmethod
    def generate_params(string, params):

        result_string = ''
        result_string += string
        for k, v in params.items():
            if k in msudrf_params_dict:
                result_string += '&{0}={1}'.format(msudrf_params_dict[k], v)
        return result_string

    def get_cases(self, codex, entry_date_from=None, articles_list=None):
        # получаем дела по инстанции, типу производства

        courts = Court.objects.filter(site_type=4)

        if articles_list:
            articles = CodexArticle.objects.get_from_list(articles_list, codex=codex)
        else:
            articles = CodexArticle.objects.filter(codex=codex, active=True)

        for court in courts:
            for article in articles:  # похоже, мы не можем искать сразу по списку статей

                url = self.generate_params()
                MsudrfParser(url=url, codex=codex).save_cases()
