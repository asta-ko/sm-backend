import pymorphy2

morph = pymorphy2.MorphAnalyzer()

import pandas as pd

dfru = pd.read_csv('russian_names.csv')

ru_male_names = set(dfru[dfru['Gender'] == 'М']['Name'])
ru_female_names = set(dfru[dfru['Gender'] == 'Ж']['Name'])

male_2_endings = ['ов', 'ий', 'ев', 'ин']
female_2_endings = ['ая', 'ва', 'на']


def get_gender_score(name, surname):
    gender_score = 0

    if name and name in ru_female_names:
        gender_score += 1

    if surname[-2:] in female_2_endings:
        gender_score += 1

    if name and name in ru_male_names:
        gender_score -= 1

    if surname[-2:] in male_2_endings:
        gender_score -= 1

    return gender_score


def normalize_name(name):
    name = name.replace('ё', 'е').replace('  ', ' ')
    lowername = name.lower()
    name_list = lowername.split(' ')
    if len(name_list) != 3 or '"' in lowername:
        return name

    if name_list[1][-1] != '.':
        name_list[1] = name_list[1][0].upper() + '.'
    if name_list[2][-1] != '.':
        name_list[2] = name_list[2][0].upper() + '.'
    normalized_name = f'{name_list[0].capitalize()} {name_list[1]}{name_list[2]}'
    return normalized_name[:149]


def get_gender(first_name, last_name):
    gender = get_gender_score(first_name, last_name)

    if gender > 0:
        gender_letter = 'f'
    elif gender == 0:
        gender_letter = 'na'
    elif gender < 0:
        gender_letter = 'm'
    print(last_name, first_name or '-', gender_letter)

    if gender > 0:
        return 1
    elif gender == 0:
        return None
    elif gender < 0:
        return 2


def parse_name(name):

    def is_first_name(parsed_word):
        return any('Name' in p.tag for p in parsed_word)

    name = name.lower().replace('ё', 'е')

    if '.' in name:
        return (), None  # , None, None
    name_list = name.split(' ')

    if len(name_list) != 3:
        return (), None

    if is_first_name(morph.parse(name_list[1])):
        first_name = name_list[1].capitalize()
        last_name = name_list[0].capitalize()
        middle_name = name_list[2].capitalize()

        return last_name, first_name, middle_name
    return ()

# def create_zip(name, text):
#     with open(os.path.join(PROJ_DIR, "_tmp_file_"), "w+") as f:
#         f.write(text)
#
#     zf = zipfile.ZipFile(os.path.join(PROJ_DIR, "%s.zip" % name), "w",
#                          zipfile.ZIP_DEFLATED)
#     zf.write(os.path.join(PROJ_DIR, "_tmp_file_"), "/file.txt")
#     zf.close()
