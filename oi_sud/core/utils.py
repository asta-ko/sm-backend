import re
from urllib.parse import parse_qs, urlparse


def get_query_key(url, field):
    try:
        return parse_qs(urlparse(url).query)[field][0]
    except KeyError:
        return ''


nullable = {'null': True, 'blank': True}


def get_city_from_address(address_string):
    m = re.search(r'((г|п|д|с|а|пгт|гор|пос|дер|ст)\.\s*[А-Яа-я-\s0-9ё]+),', address_string)
    if m:
        return m.group(1)
    m = re.search(r'((город|деревня|поселок|село)\s*[А-Яа-я-\s0-9ё]+),', address_string)
    if m:
        return m.group(1)
    print('Nothing found, address string ', address_string)


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]
