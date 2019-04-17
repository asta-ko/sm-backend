import pytest
from oi_sud.courts.parser import courts_parser, moscow_courts_parser
from oi_sud.courts.models import Court, Judge
from django.conf import settings


def test_courts_regions():
    courts_parser.get_regions()

@pytest.mark.django_db
def test_courts_save():
    courts_parser.save_courts(limit=10)
    assert len(Court.objects.all()) == 10

@pytest.mark.django_db
def test_save_judges():
    courts_parser.save_courts(limit=1)
    c = Court.objects.all().first()
    courts_parser.get_and_save_judges(c)
    assert len(Judge.objects.all())


@pytest.mark.django_db
def test_judges_two():
    courts_parser.save_courts(limit=100)
    c = Court.objects.filter(site_type=2).first()
    courts_parser.parse_judges_type_two(c)

#@pytest.mark.django_db
def test_moscow_get_phone():
    moscow_courts_parser.get_phone()
    asd

@pytest.mark.django_db
def test_moscow_save_courts():
    moscow_courts_parser.save_courts()
    print(Court.objects.all())
    assert len(Court.objects.all())

