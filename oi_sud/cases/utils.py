def normalize_name(name):
    name = name.replace('ё','е')
    lowername = name.lower()
    name_list = lowername.split(' ')
    if len(name_list) != 3 or '"' in lowername:
        return name
    if name_list[1][-1] != '.':
        name_list[1] = name_list[1][0].upper() + '.'
    if name_list[2][-1] != '.':
        name_list[2] = name_list[2][0].upper() + '.'
    normalized_name = f'{name_list[0].capitalize()} {name_list[1]}{name_list[2]}'
    return normalized_name

def parse_name_and_get_gender(name):
    import pymorphy2
    first_name = None
    last_name = None
    middle_name = None
    gender = None
    prob_thresh = 0.8
    morph = pymorphy2.MorphAnalyzer()
    def most_common(lst):
        return max(set(lst), key=lst.count)
    def is_first_name(parsed_word):
        return any('Name' in p.tag for p in parsed_word)
    # def is_last_name(parsed_word):
    #     return any('Surn' in p.tag for p in parsed_word)
    # def is_middle_name(parsed_word):
    #     return any('Patr' in p.tag for p in parsed_word)

    name = name.lower().replace('ё','е')

    if '.' in name:
        return (), None # , None, None
    name_list = name.split(' ')
    if len(name_list) != 3:
        return (), None

    genders = []
    parsed_name_list = [morph.parse(x) for x in name_list]
    for word in parsed_name_list:
        genders.append(word[0].tag.gender)

    gender = most_common(genders)
    if gender == 'masc':
        gender = 2
    elif gender == 'femn':
        gender = 1
    elif gender == 'neut':
        gender = None
    if is_first_name(parsed_name_list[1]):
        first_name = name_list[1].capitalize()
        last_name = name_list[0].capitalize()
        middle_name = name_list[2].capitalize()
        return (last_name, first_name, middle_name), gender
    return (), gender


