import editdistance
import pandas as pd
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

ru_male_names = pd.read_csv('ru_male_names.csv')
ru_female_names = pd.read_csv('ru_female_names.csv')


def get_gender_score(name, surname):
    male_2_endings = ['ов', 'ий', 'ев', 'ин']
    female_2_endings = ['ая', 'ва', 'на']

    gender_score = 0

    if name and (ru_female_names['0'] == name).any():
        gender_score += 1

    if surname[-2:] in female_2_endings:
        gender_score += 1

    if name and (ru_male_names['0'] == name).any():
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


def get_or_create_from_name(name, region, model, gender_needed=True):
    names = parse_name(name)
    normalized_name = normalize_name(name)
    if len(names) == 3 and model.objects.filter(region=region, last_name=names[0], first_name=names[1],
                                                middle_name=names[2]).exists():  # Совпадают регион и ФИО полностью
        return model.objects.filter(region=region, last_name=names[0], first_name=names[1],
                                    middle_name=names[2]).first()
    elif model.objects.filter(name_normalized=normalized_name,
                              region=region).exists():  # Совпадают регион, фамилия и инициалы
        qs = model.objects.filter(name_normalized=normalized_name, region=region)
        if not len(names):  # не можем проверить, отдаем первое совпадение
            return qs.first()
        else:
            for d in qs:
                if d.first_name and d.middle_name:
                    e = editdistance.eval(f'{names[1]} {names[2]}', f'{d.first_name} {d.middle_name}')
                    if e <= 3:  # проверяем, что это то же самое имя и отчество и учитываем возможность опечаток
                        return d
            return qs.first()  # если не можем проверить, берем первое попавшееся
    else:

        d_dict = {
            'region': region,
            'name_normalized': normalized_name
        }

        gender = None

        if len(names) == 3:
            d_dict['last_name'] = names[0]
            d_dict['first_name'] = names[1]
            d_dict['middle_name'] = names[2]
            if gender_needed:
                gender = get_gender(names[1], names[0])
        elif gender_needed:
            gender = get_gender(None, normalized_name.split(' ')[0])

        if gender_needed and gender:
            d_dict['gender'] = gender

        item = model(**d_dict)
        item.save()
        return item
