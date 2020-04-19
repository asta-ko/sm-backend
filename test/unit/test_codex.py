import pytest
from oi_sud.codex.models import CodexArticle


#@pytest.mark.skip
@pytest.mark.django_db
def test_from_list(koap_articles, uk_articles):
    articles = CodexArticle.objects.get_from_list(['19.3 ч.1'])
    assert (len(articles))


