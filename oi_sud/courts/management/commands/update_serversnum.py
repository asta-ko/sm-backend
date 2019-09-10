import requests
from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court
from oi_sud.courts.parser import courts_parser
from oi_sud.core.parser import CommonParser
from bs4 import BeautifulSoup


class Command(BaseCommand):

    def handle(self, *args, **options):
        for court in Court.objects.all():
            #print(court.title)
            url = court.url + '/modules.php?name=sud_delo'
            parser = CommonParser()
            text, status = parser.send_get_request(url)
            if 'Выберите сервер' in text:
                page = BeautifulSoup(text, 'html.parser')
                ul = page.find('ul', class_='statUl')
                links = ul.findAll('a')
                servers_num = len(links)
                court.servers_num = servers_num
                print(court.title, servers_num)
                court.save()

            else:
                continue

