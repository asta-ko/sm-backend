import csv
import os
import sys

from django.core.management.base import BaseCommand
from oi_sud.core.consts import region_choices
from oi_sud.courts.models import Court


class Command(BaseCommand):

    def handle(self, *args, **options):

        def parse_row(row):

            region_dict = dict((y, x) for x, y in region_choices)

            court_dict = {}

            court_dict['title'] = row[0]

            court_dict['type'] = 4

            court_dict['instance'] = 1

            court_dict['url'] = row[2]

            court_dict['site_type'] = 4

            if row[1] and region_dict.get(row[1]) is not None:
                court_dict['region'] = region_dict[row[1]]

            if row[4]:
                court_dict['full_address'] = row[4]

            if row[3]:
                phones = row[3]
                phone_code = phones.split(')')[0] + ')'
                phones = phones.replace(phone_code + ' ', '').replace(phone_code, '').replace(') ', '), ')
                court_dict['phone_numbers'] = [f'{phone_code}{x}'[:25] for x in phones.split(', ')]
            else:
                court_dict['phone_numbers'] = []

            if row[5] and row[5] != 'Не указан':
                court_dict['email'] = row[5].split(' ')[0]

            return court_dict

        # Court.objects.all().delete()

        path = os.path.join(sys.path[0], 'oi_sud/courts/management/commands/mirsud.csv')
        with open(path) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=';')
            for row in readCSV:
                try:
                    print(row)
                    if 'msudrf' not in row[2]:
                        continue
                    court_dict = parse_row(row)
                    court = Court.objects.create(**court_dict)
                    print(court)
                except:
                    pass
