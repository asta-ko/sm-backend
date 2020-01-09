import re
import pymorphy2


class KoapPenaltyExtractor(object):


    def process(self, decision_text):  # убрать temp_table после отладки
        '''находит в тексте судебного решения информацию о решении, п ри штрафе определяет сумму штрафа'''

        decision_text = re.sub('\n|\r|\s+', ' ', decision_text)  # убираем лишние пробелы и переносы строк

        postanovil_pattern = re.compile(
            r"[Пп]\s?[Оо]\s?[Сс]\s?[Тт]\s?[Аа]\s?[Нн]\s?[Оо]\s?[Вв]\s?[Ии]\s?[Лл]\s?[Аа]?")

        reshil_pattern = re.compile(r"[Рр]\s?[Ее]\s?[Шш]\s?[Ии]\s?[Лл]\s?[Аа]?")

        opredelil_pattern = re.compile(r"[Оо]\s?[Пп]\s?[Рр]\s?[Ее]\s?[Дд]\s?[Ее]\s?[Лл]\s?[Ии]\s?[Лл]\s?[Аа]?")

        # интересующая нас информация идет после слов (суд или судья) постановил и т.д. - отрезаем все остальное

        patterns = [postanovil_pattern, reshil_pattern, opredelil_pattern]
        for pattern in patterns:
            if re.search(pattern, decision_text):
                decision_text = re.split(pattern, decision_text)[-1]
                break



        # в решениях с таким текстом -- штраф. убираем лишнее, чтобы не путать
        for no_arrest in ['либо административный арест на',
                          'либо назначить наказание в виде административного ареста',
                          'в качестве одной из мер административного наказания административный арест']:
            decision_text = re.sub(no_arrest, '', decision_text)

        # записываем текст для дальнейшего просмотра и дебаггинга
        decision_text_to_view = decision_text

        # и переводим в ловеркейс для более удобной работы
        decision_text = decision_text.lower()

        # шаблон результата на выходе
        result = {'returned': False,
                  'cancelled': False,
                  'deportation': False,
                  'forward': False,
                  'fine': {},
                  'arrest': {},
                  'works': {},
                  'could_not_process': False}

        # определяем нужные в дальнейшем переменные
        fine_not_found, arrest_not_found = True, True

        # проверяем, не было ли дело возвращено
        pattern_vozvr = re.compile \
            (r'в(озвратить|ернуть).*(протокол|дело|материал.?|постановление)|(дело|протокол|постановление|материал.?).*(возвратить|вернуть)')
        if pattern_vozvr.search(decision_text) != None:
            result['returned'] = True
            return result  # сразу отдаем результат
        # проверяем, не было ли дело прекращено
        pattern_prekr = re.compile(r'[П|п]роизводство.*прекратить|[П|п]рекратить.*производство')
        if pattern_prekr.search(decision_text) != None:
            result['cancelled'] = True
            return result  # сразу отдаем результат
        if 'подведомственности' in decision_text:
            result['forward'] = True
            return result

        # получаем информацию о штрафе

        try:

            if 'штраф' in decision_text:
                fine_num, fine_not_found, fine_hidden = self.get_fine(decision_text)
                if fine_num or fine_hidden:
                    result['fine'] = {'num': int(fine_num), 'is_hidden': fine_hidden}

            # если нет информации о штрафе, получаем информацию об аресте
            if fine_not_found and 'арест' in decision_text:
                arrest_days, arrest_not_found, arrest_hidden = self.get_arrest(decision_text)
                if arrest_days or arrest_hidden:
                    result['arrest'] = {'num': int(arrest_days), 'is_hidden': arrest_hidden}

            # если нет информации о штрафе или об аресте, ищем обязательные работы
            if fine_not_found and arrest_not_found and (
                    'обязательных работ' in decision_text or 'обязательные работы' in decision_text):
                works_hours, works_not_found, works_hidden = self.get_compulsory_works(decision_text)
                if works_hours or works_hidden:
                    result['works'] = {'num': int(works_hours), 'is_hidden': works_hidden}

            # проверяем, есть ли информация о выдворении
            if 'выдвор' in decision_text:
                result['deportation'] = True
        except Exception as e:
            print('error parsing: '+e.text)

        # проверяем, что мы получили какие-то данные, и если нет, прописываем ошибку в словарь результата
        is_result_empty = True
        for k, v in result.items():
            if v:
                is_result_empty = False
                break
        if is_result_empty:
            result['could_not_process'] = True
            # print(decision_text)

        return result



    @staticmethod
    def get_num_from_text(fine_txt):

        numdict = {'один': '1', 'одна': '1', 'одни': '1', 'два': '2', 'двое': '2', 'три': '3', 'трое': '3',
                   'четыре': '4', 'пять': '5', 'шесть': '6', 'семь': '7',
                   'восемь': '8', 'девять': '9', 'десять': '10', 'одиннадцать': '11', 'двенадцать': '12',
                   'тринадцать': '13', 'четырнадцать': '14', 'пятнадцать': '15', 'шестнадцать': '16',
                   'семнадцать': '17', 'восемнадцать': '18', 'девятнадцать': '19', 'двадцать': '20',
                   'тридцать': '30', 'сорок': '40', 'пятьдесят': '50', 'шестьдесят': '60', 'семьдесят': '70',
                   'восемьдесят': '80', 'девяносто': '90', 'сто': '100', 'двести': '200', 'триста': '300',
                   'четыреста': '400', 'пятьсот': '500', 'шестьсот': '600', 'семьсот': '700',
                   'восемьсот': '800', 'девятьсот': '900'}

        morph = pymorphy2.MorphAnalyzer()

        txt_num = fine_txt.split(' ')
        num = 0
        for i in txt_num:
            if not i:
                continue
            if not 'тысяч' in i:
                # приводим числительное в именительный падеж

                i_norm = morph.parse(i)[0].normal_form
                try:
                    n = numdict[i_norm]
                except KeyError:
                    return None
                num += int(n)
            else:
                if num > 0:
                    num = num * 1000
                else:
                    num += 1000
        if num:
            return num

    def get_compulsory_works(self, decision_text):
        pattern = re.compile(
            r'в виде обязательных работ (на(?! срок)|на срок|сроком ?н?а?в?)?(?P<works_data>.{,40})(час(а|ов)|>|\*|&gt;|\.\.|--)')
        works_hours = None
        not_found = True
        hidden = False

        if pattern.search(decision_text):
            works_data = pattern.search(decision_text).group('works_data')
            pattern_hidden = re.compile(r'данные изъяты|_|\.|\*|-')
            if pattern_hidden.search(works_data):
                hidden = True
                return works_hours, not_found, hidden
            pattern_num = re.compile(r'(\d+)')
            pattern_txt = re.compile(r'\(?([а-я\.|\s]+)\)?')
            if pattern_num.search(works_data):
                works_hours = int(pattern_num.search(works_data).group(1))  # сумма штрафа числом
            elif pattern_txt.search(works_data):
                txt = pattern_txt.search(works_data).group(1)
                txt.replace('осемь' ,'восемь')
                works_hours = self.get_num_from_text(txt)
            else:
                hidden = True
        return works_hours, not_found, hidden

    def get_arrest(self, decision_text):

        patterns = [re.compile(
            r'в виде( административного)? ареста,? (на(?! срок)|на срок ?в?|сроком ?н?а?в?)?(?P<arrest_data>.{,40})(сут(ки|ок)|>|\*|&gt;|\.\.|--)'),
            re.compile(
                r'сроком( на)? (?P<arrest_data>.+)(сут(ки|ок)|>|\*|&gt;|\.\.|--)'),
            re.compile(r'наказани.( в виде)? (?P<arrest_data>.+)сут(ки|ок) (административного )?ареста'),
            re.compile
                (r' подвергнуть( его| её)? административному аресту (на(?! срок)|на срок ?в?|сроком ?н?а?в?)(?P<arrest_data>.{,40})(сут(ки|ок)|>|\*|&gt;|\.\.|--)'),
            re.compile(
                r'наложить( административный)? арест на (срок)?(?P<arrest_data>.{,40})(сут(ки|ок)|>|\*|&gt;|\.\.|--)')]

        arrest_data = None
        arrest_days = None
        not_found = True
        hidden = False

        for pattern in patterns:
            if pattern.search(decision_text):
                arrest_data = pattern.search(decision_text).group('arrest_data')
                break

        if arrest_data:
            not_found = False
            pattern_hidden = re.compile(r'данные изъяты|_|\.|\*|-|…|№')
            if pattern_hidden.search(arrest_data):
                hidden = True
                return arrest_days, not_found, hidden
            pattern_num = re.compile(r'(\d+)')  # сумма штрафа числом
            pattern_txt = re.compile(r'\(?([а-я\.|\s]+)\)?')  # сумма штрафа словами
            if pattern_num.search(arrest_data):
                arrest_days = int(pattern_num.search(arrest_data).group(1))  # сумма штрафа числом
            elif pattern_txt.search(arrest_data):
                txt = pattern_txt.search(arrest_data).group(1)
                txt.replace('осемь', 'восемь')
                arrest_days = self.get_num_from_text(txt)
            else:
                hidden = True

        return arrest_days, not_found, hidden

    def get_fine(self, decision_text):

        pattern = re.compile(
            r'штраф(а|у|ом)?,? (в доход государства )?(в сумме|в размере|размером|в размер|в)? ?(?P<fine>.+?) ?руб')
        pattern_2 = re.compile(r'наказание в виде (?P<fine>.+?) ?руб')
        hidden_pattern = re.compile(
            r'штраф(а|у|ом)? (в доход государства )?(в сумме|в размере|размером|в размер)')
        hidden_pattern_2 = re.compile(r'штраф(а|у|ом)? в? ?(<данные изъяты>|<?\.\.\.>?)')

        fine_num = None
        not_found = True
        hidden = False
        fine = None
        # находим в строке с размером штрафа суммы, написанные цифрами, и суммы, написанные буквами
        if pattern.search(decision_text):
            fine = pattern.search(decision_text).group('fine')
        elif pattern_2.search(decision_text):
            fine = pattern_2.search(decision_text).group('fine')

        if fine:
            not_found = False

            fine = re.sub('\.', '', fine)  # убираем точки
            fine = fine.replace(' 00', '00')

            pattern_num = re.compile(r'(\d+)')  # сумма штрафа числом
            pattern_txt = re.compile(r'\(([а-я\.|\s]+)\)')  # сумма штрафа словами

            if pattern_num.search(fine):
                fine_num = pattern_num.search(fine).group(1)  # сумма штрафа числом

            if not fine_num or int(fine_num) < 50:
                fine_num = None

                if pattern_txt.search(fine):
                    fine_txt = pattern_txt.search(fine).group(1)  # сумма штрафа словами в скобках
                    fine_txt.replace('осемь', 'восемь')
                    fine_num = self.get_num_from_text(fine_txt)
            if not fine_num:
                hidden = True

        elif hidden_pattern.search(decision_text.lower()) or hidden_pattern_2.search(decision_text.lower()):
            not_found = False
            hidden = True
        return fine_num, not_found, hidden

kp_extractor = KoapPenaltyExtractor()