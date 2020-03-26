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


class CORSMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"

        return response


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        print(self.set_current - self.intersect, 'added')
        return self.set_current - self.intersect

    def removed(self):
        print(self.set_past - self.intersect, 'removed')
        return self.set_past - self.intersect

    def changed(self):
        print(set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o]), 'changed')
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

    def get_all_diff_keys(self):
        d = [self.added(), self.removed(), self.changed()]
        return list(set().union(*d))
