import logging
import re
import time
from datetime import timedelta
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from dateparser.conf import settings as dateparse_settings
from django.utils.html import strip_tags
from django.utils.timezone import get_current_timezone
from oi_sud.cases.consts import *
from oi_sud.cases.models import Case
from oi_sud.cases.parsers.main import CourtSiteParser
from oi_sud.codex.models import CodexArticle
from oi_sud.core.parser import CommonParser
from oi_sud.core.utils import get_query_key
from oi_sud.courts.models import Court

logger = logging.getLogger(__name__)

dateparse_settings.TIMEZONE = str(get_current_timezone())
dateparse_settings.RETURN_AS_TIMEZONE_AWARE = False

event_types_dict = {y: x for x, y in dict(EVENT_TYPES).items()}
event_result_types_dict = {y: x for x, y in dict(EVENT_RESULT_TYPES).items()}
result_types_dict = {y: x for x, y in dict(RESULT_TYPES).items()}
appeal_result_types_dict = {y: x for x, y in dict(APPEAL_RESULT_TYPES).items()}


class RFCourtSiteParser(CourtSiteParser):

    def get_all_cases_urls(self):

        # получаем урлы всех интересующих нас дел в данном суде

        if self.court.servers_num == 1:
            return self.get_cases_urls()
        else:
            return self.get_all_cases_from_multiple_servers()

    def get_all_cases_from_multiple_servers(self):

        # обрабатываем кейс, когда у одного суда есть два сервера

        all_urls = []
        for n in range(1, self.court.servers_num + 1):
            new_params = f'srv_num={str(n)}&case__num_build={str(n)}'
            url = self.url.replace('srv_num=1', new_params)
            all_urls += self.get_cases_urls(url=url)
        return all_urls

    def get_cases_urls(self, url=None):
        # Получаем все урлы дел в данном суде стандартно

        if not url:
            url = self.url
        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            logging.error(f"GET error: unable to get rf cases - {status_code} {url}")
            return None
        first_page = BeautifulSoup(txt, 'html.parser')
        pages_number = self.get_pages_number(first_page)  # TODO CHANGE
        all_pages = [first_page, ]
        pages_urls = None

        if pages_number != 1:
            if self.court.site_type == 2:
                pages_urls = [f'{url}&_page={p}' for p in range(2, pages_number + 1)]
            elif self.court.site_type == 1:
                pages_urls = [f'{url}&page={p}' for p in range(2, pages_number + 1)]

            for url in pages_urls:
                txt, status_code = self.send_get_request(url)
                if status_code != 200:
                    logging.error(f"GET error: rf cases - {status_code} {url}")
                    continue
                page = BeautifulSoup(txt, 'html.parser')
                all_pages.append(page)

        all_cases_urls = []

        for page in all_pages:
            try:
                urls = self.get_cases_urls_from_list(page)
                urls = [self.url.replace('/modules.php', '').split('?')[0] + u for u in urls]
                all_cases_urls += urls
            except AttributeError:
                pass
        if not all_cases_urls:
            logger.debug('Getting rf cases... Got no cases urls')
        else:
            logger.debug(f'Getting rf cases... Got {len(all_cases_urls)} cases urls')

        return all_cases_urls

    def get_koap_article(self, raw_string):
        # получаем объекты статей КОАП из строки, полученной из карточки дела

        m = re.search(r'КоАП:\sст\.\s([0-9\.]+)\s?ч?\.?([0-9\.]*)', raw_string)

        if m:
            article = m.group(1)
            part = m.group(2)
            if part == '':
                part = None
            codex_article = CodexArticle.objects.filter(codex='koap', article_number=article, part=part).first()
            if codex_article:
                return [codex_article]
        return []

    def get_uk_articles(self, raw_string):
        # получаем объекты статей УК из строки, полученной из карточки дела
        raw_list = list(set(raw_string.replace('УК РФ', '').split(';')))
        codex_articles = []
        for item in raw_list:
            codex_article = None
            item = item.strip()
            m = re.search(r'ст\.([0-9\.]+)\s?ч?\.?([0-9\.]*)', item)
            if m:
                article = m.group(1)
                part = m.group(2)
                if part == '':
                    part = None
                codex_article = CodexArticle.objects.filter(codex='uk', article_number=article, part=part).first()
            if codex_article:
                codex_articles.append(codex_article)
        return codex_articles

    def parse_events(self, events_trs, tr_head):
        # получаем события в деле

        events = []

        indeces = {
            'Наименование события': None,
            'Дата': None,
            'Дата события': None,
            'Время': None,
            'Время события': None,
            'Зал судебного заседания': None,
            'Результат': None,
            'Результат события': None
        }

        types = {
            'type': ['Наименование события'],
            'date': ['Дата', 'Дата события'],
            'time': ['Время', 'Время события'],
            'courtroom': ['Зал судебного заседания', 'Зал'],
            'result': ['Результат события', 'Результат']
        }

        while tr_head[0] != 'Наименование события':
            tr_head = tr_head[1:]

        for item in indeces.keys():
            if item in tr_head:
                indeces[item] = tr_head.index(item)

        for tr in events_trs:
            event = {}
            tds = tr.findAll('td')

            for k, v in types.items():
                for item in v:
                    if indeces.get(item) is not None and len(tds) > indeces.get(item):
                        text = tds[indeces.get(item)].text.replace('\xa0', '').strip()
                        if text:
                            event[k] = text
                            continue

            if event.get('type'):
                events.append(event)

        return events

    def parse_defenses(self, el):
        # Получаем имя обвиняемого и статьи (может быть несколько)

        defenses = []
        defendants_hidden = False
        title_tr = None
        person_index = None
        codex_articles_index = None
        trs = el.findAll('tr')

        for index, tr in enumerate(trs):

            tr_text = tr.text

            if 'ФИО' in tr_text or 'Фамилия' in tr_text or 'статей' in tr_text:
                title_tr = tr

        if not title_tr:
            title_tds = el.findAll('td', attrs={'align': 'center'})
            if not title_tds:
                title_tds = el.findAll('td', {'style': 'text-align:center'})
            if not title_tds:
                title_tds = el.findAll('td', {'style': 'text-align:center;'})
        else:
            title_tds = title_tr.findAll('td')

        for index, td in enumerate(title_tds):
            td_text = td.text.lower()
            if 'фио' in td_text or 'фамилия' in td_text:
                person_index = index
            if 'статей' in td_text:
                codex_articles_index = index
        # получаем адвокатов и защитников
        advocates = []
        trs_advocates = [tr for tr in trs if
                         'адвокат' in tr.text.lower() or 'защитник' in tr.text.lower() or 'представитель' in tr.text.lower()]
        for tr in trs_advocates:
            tds = tr.findAll('td')
            if len(tds) > person_index and len(tds) > codex_articles_index:
                advocate = tds[person_index].text.strip()
                advocates.append(advocate)

        # получаем прокуроров
        prosecutors = []
        trs_prosecutors = [tr for tr in trs if 'прокурор' in tr.text.lower()]
        for tr in trs_prosecutors:
            tds = tr.findAll('td')
            if len(tds) > person_index and len(tds) > codex_articles_index:
                prosecutor = tds[person_index].text.strip()
                prosecutors.append(prosecutor)

        #  получаем ответчиков и составляем сущность defense с каждым из них
        #  (если нашлись защитники или прокуроров, сразу добавляем)
        for tr in trs:

            tr_text = tr.text.lower()
            if 'информация скрыта' in tr_text:
                defendants_hidden = True

            if 'фио' in tr_text or 'статей' in tr_text \
                    or 'фамилия' in tr_text \
                    or 'информация скрыта' in tr_text \
                    or 'адвокат' in tr_text \
                    or 'защитник' in tr_text \
                    or 'представитель' in tr_text \
                    or 'прокурор' in tr_text:
                continue

            tds = tr.findAll('td')
            if len(tds) > person_index and len(tds) > codex_articles_index:
                defendant = tds[person_index].text.strip()
                codex_articles = tds[codex_articles_index].text.strip()
                if codex_articles == '':
                    raise Exception('Defendant has no articles')
                defenses.append({'defendant': defendant, 'codex_articles': codex_articles, 'advocates': advocates,
                                 'prosecutors': prosecutors})
        return defenses, defendants_hidden


class FirstParser(RFCourtSiteParser):

    # в системе судрф есть 2 типа сайтов судов, здесь мы обрабатываем первый (как https://krv--spb.sudrf.ru)

    def get_pages_number(self, page):
        # получаем число страниц с делами
        pagination_a = page.find('a', attrs={'title': 'На последнюю страницу списка'})
        if not pagination_a:
            return 1
        else:
            last_page_href = pagination_a['href']
            pages_number = int(get_query_key(last_page_href, 'page'))
            return pages_number

    def get_cases_urls_from_list(self, page):
        # получаем урлы карточек дел из страницы поиска
        urls = []
        tds = page.find('table', id='tablcont').findAll('td', attrs={
            'title': 'Для получения справки по делу, нажмите на номер дела'
        })
        for td in tds:
            href = td.find('a')['href']
            if Case.objects.filter(url=href).exists():
                continue
            urls.append(href + '&nc=1')

        return urls

    def get_result_text_url(self, page):
        # получаем урл на текст решения
        if not self.court:
            return
        ths = page.find('div', id='cont1').findAll('th')
        for th in ths:
            a = th.find('a')
            if a and a['href']:
                return self.court.url + a['href'] + '&nc=1'
        return

    def get_result_text(self, url):
        # получаем текст решения
        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            logging.error(f"GET error: rf case result text - {status_code} {url}")
            return None
        page = BeautifulSoup(txt, 'html.parser')
        result_text_span = page.find('span')
        if result_text_span:
            return strip_tags(result_text_span.text)
        else:
            return ''

    def get_tabs(self, page):

        def events_table(tag):
            return tag.name == 'table' and 'движение дела' in tag.text.lower()

        def defendants_table(tag):
            return tag.name == 'table' and ('стороны по делу' in tag.text.lower() or
                                            'сведения о лице' in tag.text.lower() or
                                            'ЛИЦА' in tag.text)

        def appeal_table(tag):
            return tag.name == 'table' and 'дата рассмотрения жалобы' in tag.text.lower()

        tabs = {
            'delo': page.find('div', id='cont1').find('table'),
            'events': page.find(events_table),
            'defendants': page.find(defendants_table),
            'appeal': page.find(appeal_table)
        }

        return tabs

    def get_raw_case_information(self, url):
        if '&nc=1' not in url:
            url += '&nc=1'

        self.current_url = url

        # парсим карточку дела
        case_info = {}
        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            logging.error(f"GET error: rf case - {status_code} {url}")
            return

        page = BeautifulSoup(txt, 'html.parser')

        case_info['case_number'] = page.find('div', class_='casenumber').text.replace('ДЕЛО № ', '')
        case_info['url'] = url.replace('&nc=1', '')
        case_result_text_url = self.get_result_text_url(page)
        if case_result_text_url:
            result_text = self.get_result_text(case_result_text_url)
            case_info['result_text'] = result_text
        tables = self.get_tabs(page)
        case_trs = tables['delo'].find('tr').findAll('tr')
        for tr in case_trs:
            tds = tr.findAll('td')
            if len(tds) < 2:
                continue
            val = tds[1].text
            tr_text = tr.text.lower()
            if 'уникальный идентификатор дела' in tr_text:
                case_info['case_uid'] = val
            if 'дата поступления' in tr_text:
                case_info['entry_date'] = val
            if 'номер протокола об ап' in tr_text:
                case_info['protocol_number'] = val
            if 'судья' in tr_text or 'передано в производство судье' in tr_text or 'дело находится в производстве ' \
                                                                                   'судьи' in tr_text:
                case_info['judge'] = val
            if 'дата рассмотрения' in tr_text or 'дата вынесения постановления (определения) по делу' in tr_text:
                case_info['result_date'] = val
            if 'результат рассмотрения' in tr_text:
                case_info['result_type'] = val
        case_info['events'] = []
        if tables.get('events'):
            tr_head = [x.text for x in tables['events'].findAll('td')][:10]

            trs = tables['events'].findAll('tr')[2:]

            case_info['events'] = self.parse_events(trs, tr_head)

        case_info['defenses'] = []
        if tables.get('defendants'):
            # trs = page.find('div', id='cont3').findAll('tr')
            case_info['defenses'], case_info['defendants_hidden'] = self.parse_defenses(tables['defendants'])
        if tables.get('appeal'):
            trs = tables['appeal'].findAll('tr')
            for tr in trs:
                tr_text = tr.text.lower()
                if 'дата направления дела в вышест. суд' in tr_text:
                    case_info['forwarding_to_higher_court_date'] = tr.findAll('td')[1].text.replace('\xa0', '').strip()
                if 'дата рассмотрения жалобы' in tr_text:
                    case_info['appeal_date'] = tr.findAll('td')[1].text.replace('\xa0', '').strip()
                if 'результат обжалования' in tr_text:
                    case_info['appeal_result'] = tr.findAll('td')[1].text.replace('\xa0', '').strip()
                if 'дата возврата в нижестоящий суд' in tr_text:
                    case_info['forwarding_to_lower_court_date'] = tr.findAll('td')[1].text.replace('\xa0', '').strip()

        return case_info


class SecondParser(RFCourtSiteParser):

    # в системе судрф есть 2 типа сайтов судов, здесь мы обрабатываем первый (как https://bezhecky--twr.sudrf.ru)

    def get_pages_number(self, page):
        # получаем число страниц с делами
        pagination = page.find('ul', class_='pagination')
        if pagination:
            last_page_href = pagination.findAll('li')[-2].find('a')['href']
            pages_number = int(get_query_key(last_page_href, '_page'))

            return pages_number
        else:
            return 1

    def get_cases_urls_from_list(self, page):
        # получаем урлы карточек дел из страницы поиска
        urls = []

        a_cases = page.findAll('a', class_='open-lawcase')
        for a in a_cases:
            if Case.objects.filter(url=a['href']).exists():
                continue
            urls.append(a['href'] + '&nc=1')

        return urls

    def get_raw_case_information(self, url):

        if '&nc=1' not in url:
            url += '&nc=1'

        self.current_url = url

        # парсим карточку дела
        case_info = {}
        txt, status_code = self.send_get_request(url)
        if status_code != 200:
            logging.error(f"GET error: rf case - {status_code} {url}")
            return None

        page = BeautifulSoup(txt, 'html.parser')
        case_info['case_number'] = page.find('div',
                                             class_='case-num').text.replace('дело № ', '').replace('ДЕЛО № ', '')
        case_info['url'] = url.replace('&nc=1', '')
        case_result_text_div = page.find('div', id='tab_content_Document1')
        if case_result_text_div:
            case_result_text = strip_tags(case_result_text_div)
            case_info['result_text'] = case_result_text
        case_trs = page.find('div', id='tab_content_Case').findAll('tr')
        for tr in case_trs:
            tr_text = tr.text.lower()
            tds = tr.findAll('td')
            if len(tds) < 2:
                continue
            val = tds[1].text
            if 'уникальный идентификатор дела' in tr_text:
                case_info['case_uid'] = val
            if 'дата поступления' in tr_text:
                case_info['entry_date'] = val
            if 'номер протокола об ап' in tr_text:
                case_info['protocol_number'] = val
            if 'судья' in tr_text \
                    or 'передано в производство судье' in tr_text \
                    or 'дело находится в производстве судьи' in tr_text:
                case_info['judge'] = val
            if 'дата рассмотрения' in tr_text or 'дата вынесения постановления (определения) по делу' in tr_text:
                case_info['result_date'] = val
            if 'результат рассмотрения' in tr_text:
                case_info['result_type'] = val
        case_info['events'] = []
        if page.find('div', id='tab_content_EventList'):
            events_trs = page.find('div', id='tab_content_EventList').findAll('tr')[1:]
            tr_head = [x.text for x in page.find('div', id='tab_content_EventList').findAll('td')][:10]
            case_info['events'] = self.parse_events(events_trs, tr_head)

        defense_table = page.find('div', id='tab_content_PersonList').find('table', class_='none-mobile')

        case_info['defenses'], case_info['defendants_hidden'] = self.parse_defenses(defense_table)

        return case_info


class RFCasesGetter(CommonParser):

    def __init__(self, codex):
        if isinstance(codex, int):
            codex = 'koap' if codex == 1 else 'uk'
        self.codex = codex
        self.site_params = site_types_by_codex[self.codex]

    @staticmethod
    def generate_articles_string(articles):
        # на входе список статей, на выходе get параметры для поиска
        params_string = ''
        for article in articles:
            if article.part:
                params_string += f'&lawbookarticles[]={article.article_number}+ .{article.part}'
            else:
                params_string += f'&lawbookarticles[]={article.article_number}'

        return params_string  # .replace('[]', '%5B%5D').replace(' ', '%F7')

    @staticmethod
    def generate_params(string, params_dict, params):
        result_string = ''
        formatted_params = {}
        for k, v in params.items():
            formatted_params[params_dict[k]] = v
        params_string = urlencode(formatted_params, encoding='Windows-1251')
        result_string += string + params_string
        return result_string

    def generate_url(self, court, params, instance):
        site_type = str(court.site_type)
        string = self.site_params[site_type]['string']
        delo_id, case_type, delo_table = instances_dict[self.codex][str(instance)]
        string = string.replace('DELOID', delo_id).replace('CASETYPE', case_type).replace('DELOTABLE', delo_table)
        params_dict = self.site_params[site_type]['params_dict']
        params_string = self.generate_params(string, params_dict, params)
        if instance == 2:
            params_string = params_string.replace('adm', 'adm1').replace('adm11', 'adm1')
        return court.url + params_string

    def get_moved_case_url(self, case):
        print('getting moved case url...')
        got_urls = []
        article_string = self.generate_articles_string(case.codex_articles.all())
        entry_date_from = (case.entry_date - timedelta(days=2)).strftime('%d.%m.%Y')
        entry_date_to = (case.entry_date + timedelta(days=2)).strftime('%d.%m.%Y')
        defendants = [x.name_normalized.split(' ')[0] for x in case.defendants.all()]
        for name in defendants:
            params = {'articles': article_string,
                      'entry_date_from': entry_date_from,
                      'entry_date_to': entry_date_to,
                      'last_name': name
                      }

            for attr in ['judge', 'case_uid']:
                if getattr(case, attr):
                    params[attr] = getattr(case, attr)

            url = self.generate_url(case.court, params, case.stage)

            if case.court.site_type == 2:
                url = url.replace('XXX', case.court.vn_kod)
                got_urls += SecondParser(court=case.court, stage=case.stage, codex=self.codex,
                                         url=url).get_all_cases_urls()

            elif case.court.site_type == 1:
                got_urls += FirstParser(court=case.court, stage=case.stage, codex=self.codex,
                                        url=url).get_all_cases_urls()

        got_urls = list(set(got_urls))
        if len(got_urls) == 1:
            return got_urls[0].replace('&nc=1', '')
        else:
            case.actual_url_unknown = True
            case.save(update_fields=["actual_url_unknown"])  # прерываем обновление дела, но помечаем дело
            if not got_urls:
                raise Exception('Did not found updated urls')
            elif len(got_urls) > 1:
                print('multiple_found_urls', got_urls)
                raise Exception('Found multiple updated urls')

    def get_cases(self, instance, courts_ids=None, courts_limit=None, entry_date_from=None, custom_articles=None):
        start_time = time.time()
        articles = None
        if not custom_articles:
            articles = CodexArticle.objects.filter(codex=self.codex, active=True)
        else:
            articles_list = custom_articles.split(', ')
            articles = CodexArticle.objects.get_from_list(articles_list)
            if not len(articles):
                raise Exception('Could not get custom articles')

        article_string = self.generate_articles_string(articles)

        if not courts_ids:
            courts = Court.objects.exclude(type=9)
        else:
            courts = Court.objects.filter(pk__in=courts_ids)
        if courts_limit:
            courts = courts[:courts_limit]

        all_results = {}

        for court in courts:

            try:
                params = {'articles': article_string}
                if entry_date_from:
                    params['entry_date_from'] = entry_date_from  # DD.MM.YYYY
                url = self.generate_url(court, params, instance)
                if court.site_type == 2:
                    url = url.replace('XXX', court.vn_kod)
                    result = SecondParser(court=court, stage=instance, codex=self.codex, url=url).save_cases()
                    all_results[court.title] = result
                elif court.site_type == 1:
                    result = FirstParser(court=court, stage=instance, codex=self.codex, url=url).save_cases()
                    all_results[court.title] = result

            except Exception as e:
                logger.error(f'Error getting rf cases {e}')

                court.not_available = True
                court.save()
                all_results[court.title] = 'error'
        logger.info("--- %s seconds ---" % (time.time() - start_time))
        logger.info(all_results)
        return all_results
