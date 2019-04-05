from urllib.parse import parse_qs, urlparse

def get_query_key(url, field):
    try:
        return parse_qs(urlparse(url).query)[field][0]
    except KeyError:
        return ''

nullable = {'null': True, 'blank': True}
