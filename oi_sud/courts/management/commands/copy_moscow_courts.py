from django.core.management.base import BaseCommand

from oi_sud.courts.models import Court
from oi_sud.courts.parser import courts_parser


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Court.objects.all().delete()
        moscow_courts = Court.objects.filter(region=77, type='0').order_by('title')
        Court.objects.filter(region=77, site_type='2').delete()

        old_courts_urls = ['http://babushky.msk.sudrf.ru','http://basmanny.msk.sudrf.ru','http://butyrsky.msk.sudrf.ru','http://gagarinsky.msk.sudrf.ru','http://golovinsky.msk.sudrf.ru','http://dorogomilovsky.msk.sudrf.ru','http://zamoskvoretsky.msk.sudrf.ru','http://zelenogradsky.msk.sudrf.ru','http://zuzinsky.msk.sudrf.ru','http://izmailovsky.msk.sudrf.ru','http://koptevsky.msk.sudrf.ru','http://kuzminsky.msk.sudrf.ru','http://kuncevsky.msk.sudrf.ru','http://lefortovsky.msk.sudrf.ru','http://lublinsky.msk.sudrf.ru','http://meshansky.msk.sudrf.ru','http://nagatinsky.msk.sudrf.ru','http://nikulinsky.msk.sudrf.ru','http://ostankinsky.msk.sudrf.ru','http://perovsky.msk.sudrf.ru','http://preobrazhensky.msk.sudrf.ru','http://presnensky.msk.sudrf.ru','http://savelovsky.msk.sudrf.ru','http://simonovsky.msk.sudrf.ru','http://solncevsky.msk.sudrf.ru','http://tagansky.msk.sudrf.ru','http://tverskoy.msk.sudrf.ru','http://timiryazevsky.msk.sudrf.ru','http://troitsky.msk.sudrf.ru','http://tushinsky.msk.sudrf.ru','http://hamovnichesky.msk.sudrf.ru','http://horoshevsky.msk.sudrf.ru','http://chertanovsky.msk.sudrf.ru','http://cheremushinsky.msk.sudrf.ru','http://sherbinsky.msk.sudrf.ru']
        for index, court in enumerate(moscow_courts, start=1):
            indexstr = '{:0>2d}'.format(index)
            vncode = f'77RS00{indexstr}'
            # print(vncode)
            # print(court,index)
            court.vn_kod = vncode
            court.title = court.title + ' (СТАРЫЙ САЙТ)'
            print(court.title)
            court.pk = None
            court.site_type = 2
            court.url = old_courts_urls[index-1]
            court.save()
            # ourt

