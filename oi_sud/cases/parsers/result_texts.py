import logging
import re

import pymorphy2

logger = logging.getLogger(__name__)


class KoapPenaltyExtractor(object):

    def get_resolution_text(self, decision_text):

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

        # и переводим в ловеркейс для более удобной работы
        return decision_text.lower()

    def process(self, decision_text):  # убрать temp_table после отладки
        """находит в тексте судебного решения информацию о решении, при штрафе определяет сумму штрафа"""
        decision_text = self.get_resolution_text(decision_text)
        # шаблон результата на выходе
        result = {
            'returned': False,
            'cancelled': False,
            'forward': False,
            'fine': {},
            'arrest': {},
            'works': {},
            'could_not_process': False,
            'caution': False,
            'suspension': False
        }

        # определяем нужные в дальнейшем переменные
        fine_not_found, arrest_not_found, works_not_found = True, True, True

        # проверяем, не было ли дело прекращенотит
        pattern_prekr = re.compile(
            r'([П|п]роизводств.|[Д|д]ел(о|а)).*прекратить|прекратить|[П|п]рекратить.*(производств.|дел(о|а))|'
            r'.*([П|п]роизводств.|[П|п]роизводств. по делу|[Д|д]ел(о|а)|[П|п]о делу).*подлежит прекращению'
        )
        if pattern_prekr.search(decision_text) is not None:
            result['cancelled'] = True
            return result  # сразу отдаем результат

        # не было ли дело перенаправлено
        pattern_forward = re.compile(
            r'направить.+(подсудности|для рассмотрения|подведомственности|судье|в комиссию)|'
            r'(дел(о|а)|протокол|материал.).+направить в'
        )
        if pattern_forward.search(decision_text) is not None:
            result['forward'] = True
            return result

        # проверяем, не было ли дело возвращено
        pattern_vozvr = re.compile(
            r'возвращаю|возвращается|в(озвратить|ернуть).*(протокол|дело|материал.?|постановление)|('
            r'дело|протокол|постановление|материал.?).*(возвратить|вернуть|передать)|('
            r'возвратить|вернуть|передать).*(дело|протокол|постановление|материал.?)|('
            r'протокол|дела|материал.?).*подлеж(ит|ат) возврату|('
            r'дело|протокол|постановление|материал.?)? ?'
            r'[В|в]озвращен.? сопроводительным письмом|для устранения (.+)?недостатков')
        if pattern_vozvr.search(decision_text) is not None and fine_not_found and arrest_not_found and \
                works_not_found:
            result['returned'] = True
            return result  # сразу отдаем результат

        try:

            # штраф
            if 'штраф' in decision_text:
                result['fine'] = self.get_fine(decision_text)

            elif 'арест' in decision_text:
                result['arrest'] = self.get_arrest(decision_text)

            # если нет информации о штрафе или об аресте, ищем обязательные работы
            elif 'обязательных работ' in decision_text or 'обязательные работы' in decision_text:
                result['works'] = self.get_compulsory_works(decision_text)

            # наказание в виде предупреждения
            pattern_caution = re.compile(r'в виде.+предупреждения|предупреждение|замечани')
            if pattern_caution.search(decision_text) is not None:
                result['caution'] = True

            # наказание в виде приостановления деятельности
            pattern_suspension = re.compile(r'в виде.+приостановления (деятельности|эксплуатации)')
            if pattern_suspension.search(decision_text) is not None:
                result['suspension'] = True

        except Exception as e:
            logging.error(f'Error parsing case result text: {e}')
            # logging.info(decision_text)

        # проверяем, что мы получили какие-то данные, и если нет, прописываем ошибку в словарь результата
        is_result_empty = True
        for k, v in result.items():
            if v:
                is_result_empty = False
                break
        if is_result_empty:
            result['could_not_process'] = True

        return result

    @staticmethod
    def get_num_from_text(fine_txt):

        numdict = {
            'один': '1', 'одна': '1', 'одни': '1', 'два': '2', 'двое': '2', 'три': '3', 'трое': '3',
            'четыре': '4', 'пять': '5', 'шесть': '6', 'семь': '7',
            'восемь': '8', 'девять': '9', 'десять': '10', 'одиннадцать': '11', 'двенадцать': '12',
            'тринадцать': '13', 'четырнадцать': '14', 'пятнадцать': '15', 'шестнадцать': '16',
            'семнадцать': '17', 'восемнадцать': '18', 'девятнадцать': '19', 'двадцать': '20',
            'тридцать': '30', 'сорок': '40', 'пятьдесят': '50', 'шестьдесят': '60', 'семьдесят': '70',
            'восемьдесят': '80', 'девяносто': '90', 'сто': '100', 'двести': '200', 'триста': '300',
            'четыреста': '400', 'пятьсот': '500', 'шестьсот': '600', 'семьсот': '700',
            'восемьсот': '800', 'девятьсот': '900'
        }

        morph = pymorphy2.MorphAnalyzer()

        txt_num = fine_txt.split(' ')
        num = 0
        for i in txt_num:
            if not i:
                continue
            if 'тысяч' not in i:
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

        patterns = [re.compile(
            r'(в)? виде обязательных р.бот (на (срок )?|сроком (на |в )?)?(?P<works_data>.{,40})'
            r'(час(а|ов)|>|\*|&gt;|\.\.|--)'),
            re.compile(
                r'(на (срок )?(до)?|сроком (на |в |до )?)(?P<works_data>.{,40})(час(а|ов|\.)|>|\*|&gt;|\.\.|--)'),
            re.compile(r'в виде (?P<works_data>.{,40})(час(а|ов)\)?) обязательных'),
            re.compile(r'в виде обязательных р.бот'),
            re.compile(r'наказание - (?P<works_data>.{,40})(час(а|ов)) обязательных')
        ]
        works_hours = None
        hidden = False

        for pattern in patterns:
            if pattern.search(decision_text):
                try:
                    works_data = pattern.search(decision_text).group('works_data')
                except IndexError:
                    return {'num': works_hours, 'is_hidden': True}

                pattern_hidden = re.compile(r'данные изъяты|_|\.|\*|-')
                if pattern_hidden.search(works_data):
                    return {'num': works_hours, 'is_hidden': True}

                pattern_num = re.compile(r'(\d+)')
                pattern_txt = re.compile(r'\(?([а-я\.|\s]+)\)?')

                if pattern_num.search(works_data):
                    works_hours = int(pattern_num.search(works_data).group(1))  # сумма штрафа числом
                elif pattern_txt.search(works_data):
                    txt = pattern_txt.search(works_data).group(1)
                    txt.replace('осемь', 'восемь')
                    works_hours = self.get_num_from_text(txt)
                else:
                    hidden = True

                if hidden or works_hours:
                    return {'num': works_hours, 'is_hidden': hidden}

    def get_arrest(self, decision_text):

        patterns = \
            [re.compile(r'в виде( административного)? ареста,? (на(?! срок)|на срок ?в?|сроком ?н?а?в?)'
                        r'?(?P<arrest_data>.{,40})(сут(ки|ок)|>|\*|&gt;|\.\.|--)'),
             re.compile(r'сроком( на)? (?P<arrest_data>.+)(сут(ки|ок)|>|\*|&gt;|\.\.|--)'),
             re.compile(r'наказани.( в виде)? (?P<arrest_data>.+)сут(ки|ок) (административного )?ареста'),
             re.compile(r' подвергнуть( его| её)? административному аресту (на(?! срок)|на срок ?в?|сроком ?н?а?в?)('
                        r'?P<arrest_data>.{,40})(сут(ки|ок)|>|\*|&gt;|\.\.|--)'),
             re.compile(r'наложить( административный)? арест на (срок)?(?P<arrest_data>.{,40})'
                        r'(сут(ки|ок)|>|\*|&gt;|\.\.|--)')]

        arrest_data = None
        arrest_days = None
        hidden = False

        for pattern in patterns:
            if pattern.search(decision_text):
                arrest_data = pattern.search(decision_text).group('arrest_data')
                break

        if arrest_data:
            pattern_hidden = re.compile(r'данные изъяты|_|\.|\*|-|…|№')
            if pattern_hidden.search(arrest_data):
                hidden = True
                return {'num': arrest_days, 'is_hidden': hidden}
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

        return {'num': arrest_days, 'is_hidden': hidden}

    def get_fine(self, decision_text):

        hidden_pattern = re.compile(r'штраф(а|у|ом)? в? ?(<данные изъяты>|<?\.\.\.>?)|'
                                    r'штраф(а|у|ом)? в размере (<данные изъяты>|<?\.\.\.>?)')

        patterns = [re.compile(
            r'штраф(а|у|ом)?,? (в доход государства )?(в сумме|в размере|размером|в размер|в|в виде|не менее)? ?'
            r'(?P<fine>.+?) ?руб'),
            re.compile(
                r'(в сумме|в размере|размером|в размер|не менее) ?(?P<fine>.+?) ?руб'),
            re.compile(r'наказание в виде (административного )?(штрафа )?(в размере )?(в виде )?(не менее )? ?'
                       r'(?P<fine>.+?)(\(.*\))?(руб|рублей)?(штрафа )'),
            re.compile(r'в виде (?P<fine>\d+) штрафа'),

        ]
        # сумма скрыта
        hidden_pattern_2 = re.compile(
            r'штраф(а|у|ом)? (в доход государства )?(в сумме|в размере|размером|в размер)|'
            r'штраф должен быть уплачен|'
            r'штраф следует оплатить|'
            r'штраф подлежит уплате')

        fine_num = None
        hidden = False
        fine = None
        # находим в строке с размером штрафа суммы, написанные цифрами, и суммы, написанные буквами
        for pattern in patterns:
            if pattern.search(decision_text):
                fine = pattern.search(decision_text).group('fine')

        if hidden_pattern.search(decision_text.lower()):
            hidden = True
        elif fine:
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
        # не совпало со всеми остальными шаблонами, смотрим другие возможные указания на штраф
        elif hidden_pattern_2.search(decision_text.lower()):
            hidden = True

        if fine_num or hidden:
            return {'num': fine_num, 'is_hidden': hidden}


kp_extractor = KoapPenaltyExtractor()
