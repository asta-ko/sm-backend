import numpy as np
import pandas as pd
from oi_sud.cases.models import Case
from oi_sud.cases.views import CaseFilter, DefaultFilterBackend
from oi_sud.codex.models import CodexArticle, KoapCodexArticle, UKCodexArticle
from oi_sud.core.consts import region_choices
from oi_sud.courts.models import Court
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_pandas import PandasSimpleView


class CountCasesView(APIView):

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_queryset(self):
        return Case.objects.all()

    permission_classes = (permissions.IsAdminUser,)
    filter_backends = [DefaultFilterBackend]
    filterset_class = CaseFilter

    def get(self, request, format=None):
        queryset = self.get_queryset()  # Case.objects.all()
        filtered_queryset = self.filter_queryset(queryset)

        koap_qs = filtered_queryset.filter(type=1)
        uk_qs = filtered_queryset.filter(type=2)

        if filtered_queryset.exists():
            count_all = filtered_queryset.count()
            # count_koap = filtered_queryset.filter(codex='koap')
            data = {
                'all': count_all, 'koap': {'count': koap_qs.count(), 'articles': {}},
                'uk': {'count': uk_qs.count(), 'articles': {}}
            }

            for article_number in KoapCodexArticle.objects.filter(active=True).values_list('article_number',
                                                                                           flat=True).distinct():
                # if cases_koap.filter(codex_articles__artile_number=article_number).count():

                data['koap']['articles'][article_number] = {
                    'all': koap_qs.filter(codex_articles__article_number=article_number).count()
                }
                if KoapCodexArticle.objects.filter(article_number=article_number).count() > 1:
                    for article in KoapCodexArticle.objects.filter(article_number=article_number):
                        if koap_qs.filter(codex_articles__in=[article]).count():
                            data['koap']['articles'][article_number][article.__str__()] = koap_qs.filter(
                                codex_articles__in=[article]).count()
            for article_number in UKCodexArticle.objects.filter(active=True).values_list('article_number',
                                                                                         flat=True).distinct():
                # if cases_koap.filter(codex_articles__artile_number=article_number).count():
                data['uk']['articles'][article_number] = {
                    'all': uk_qs.filter(codex_articles__article_number=article_number).count()
                }
                if UKCodexArticle.objects.filter(article_number=article_number).count() > 1:
                    for article in UKCodexArticle.objects.filter(article_number=article_number):
                        if uk_qs.filter(codex_articles__in=[article]).count():
                            data['uk']['articles'][article_number][article.__str__()] = uk_qs.filter(
                                codex_articles__in=[article]).count()
            return Response({'data': data})
        else:
            return Response([])


class FrontCountCasesView(CountCasesView):

    def get_parent_data(self):

        return [
            {
                'article': 'КОАП', 'count': self.cases_koap.count(),
                'count_first_instance': self.cases_koap.filter(
                    stage=1).count(),
                'count_second_instance': self.cases_koap.filter(stage=2).count(), 'key': 'koap',
                'description': 'Всего дел об административных правонарушениях', 'children': []
            },
            {
                'article': 'УК', 'count': self.cases_uk.count(),
                'count_first_instance': self.cases_uk.filter(stage=1).count(),
                'count_second_instance': self.cases_uk.filter(stage=2).count(), 'key': 'uk',
                'description': 'Всего уголовных дел', 'children': []
            }]

    def get_article_children(self, cases_article_qs, codex_articles, article_number):
        if KoapCodexArticle.objects.filter(article_number=article_number).count() > 1:
            children = []
            for article in codex_articles.filter(article_number=article_number):
                if self.cases_koap.filter(codex_articles__in=[article]).count():
                    children.append({
                        'article': article.__str__(), 'key': article.__str__(),
                        'count_first_instance': cases_article_qs.filter(stage=1, codex_articles__in=[
                            article]).count(),
                        'count_second_instance': cases_article_qs.filter(stage=2, codex_articles__in=[article]).count(),
                        'count': cases_article_qs.filter(codex_articles__in=[article]).count(),
                        'description': article.short_title
                    })
            return children

    def get_main_item(self, codex_type, article_number, description):

        cases_qs = None

        if codex_type == 'koap':
            cases_qs = self.cases_koap
            codex_articles = KoapCodexArticle.objects.all()
        elif codex_type == 'uk':
            cases_qs = self.cases_uk
            codex_articles = UKCodexArticle.objects.all()

        cases_article_qs = cases_qs.filter(codex_articles__article_number=article_number)
        children = []
        if codex_articles.filter(article_number=article_number).count() > 1:
            children = self.get_article_children(cases_article_qs, codex_articles, article_number)

        return {
            'article': article_number, 'key': article_number,
            'count_first_instance': cases_article_qs.filter(stage=1).count(),
            'count_second_instance': cases_article_qs.filter(stage=2).count(), 'count': cases_article_qs.count(),
            'description': description, 'children': children
        }

    def get(self, request, format=None):

        filtered_queryset = self.filter_queryset(self.get_queryset())

        self.cases_koap = filtered_queryset.filter(type=1)
        self.cases_uk = filtered_queryset.filter(type=2)

        if filtered_queryset.exists():

            data = self.get_parent_data()

            koap = []
            uk = []

            for article_number in KoapCodexArticle.objects.filter(active=True).values_list('article_number',
                                                                                           flat=True).distinct():
                description = KoapCodexArticle.objects.filter(
                    article_number=article_number).first().parent_title
                main_item = self.get_main_item('koap', article_number, description)

                koap.append(main_item)

            data[0]['children'] = koap

            for article_number in UKCodexArticle.objects.filter(active=True).values_list('article_number',
                                                                                         flat=True).distinct():
                description = UKCodexArticle.objects.filter(
                    article_number=article_number).first().parent_title
                main_item = self.get_main_item('uk', article_number, description)

                koap.append(main_item)

            data[1]['children'] = uk

            return Response({'data': data})
        else:
            return Response({'data': []})


all_metrics = {
    'entried': 'Всего поступило',
    'has_result_text': 'Есть текст решения',
    # 'moscow_result_text_error': 'Ошибка при получении решения',
    'resulted': 'Рассмотрено',
    'koap1_result_was_punished': 'Назначено наказание',
    'koap1_result_forwarded': 'Направлено по подвед.',
    'koap1_result_cancelled': 'Прекращено',
    'koap1_result_returned': 'Возврат',
    # 'penalties_all': 'Всего дел с информацией о наказании',
    'penalties_errors': 'Наказаний не удалось обработать',
    'penalties_fines_all': 'Всего штрафов',
    'penalties_arrests_all': 'Всего арестов',
    'penalties_works_all': 'Всего обязательных работ',
    'penalties_hidden': 'Наказания зацензурены',
    'penalties_fines_hidden': 'Всего штрафов зацензурено',
    'penalties_arrests_hidden': 'Всего арестов зацензурено',
    'penalties_works_hidden': 'Всего работ зацензурено',
    'defendants_hidden': 'Ответчики зацензурены',
    'defendants_f': 'Пол Ж',
    'defendants_m': 'Пол М',
    'defendants_na': 'Пол ?'
}

RESULTS_FORWARDED = ['Дело присоединено к другому делу', 'Направлено по подведомственности',
                     'Вынесено определение о передаче дела по подведомственности (ст 29.9 ч.2 п.2 и ст 29.4 ч.1 п.5)',
                     'Вынесено определение о передаче дела судье, в орган, должностному лицу, уполномоченному ...']
RESULTS_RETURNED = ['Возвращено',
                    'Вынесено определение о возвращении протокола об АП и др. материалов дела в орган, долж. лицу ... '
                    'в случае составления протокола и оформления других материалов дела неправомочными лицами, ...']


class DataView(PandasSimpleView):

    def get_list_param(self, param_name):
        list_param_name = param_name + '[]'
        item = self.request.query_params.getlist(list_param_name) or self.request.GET.get(param_name)
        if item and not isinstance(item, list):
            return [item, ]
        elif item:
            return item
        else:
            return []

    def process_get(self, request):
        years = self.get_list_param('years')
        article = self.get_list_param('article')
        regions = self.get_list_param('regions')
        metrics = self.get_list_param('metrics')
        stage = request.GET.get('stage')
        type = request.GET.get('type')

        def can_use_metric(x):
            if type == '2' and 'penalties' in x:
                return False
            if type == '2' and 'koap' in x:
                return False
            if stage == '2' and 'koap1' in x:
                return False
            if stage == '1' and 'koap2' in x:
                return False
            return True

        metrics_list = [x for x in all_metrics.keys() if can_use_metric(x)]
        if metrics:
            metrics_list = [x for x in metrics_list if x in metrics]
        return years, article, regions, stage, metrics_list, type

    @staticmethod
    def get_metric(name, articles_string, region=None, year=None, stage=None, type=None, court=None):  # NOQA
        filters = {}
        if year and not name == 'resulted':
            filters['entry_date__year'] = year
        if stage:
            filters['stage'] = int(stage)
        if type:
            filters['type'] = type
        if court:
            filters['court'] = court
        if articles_string:
            articles = CodexArticle.objects.get_from_list([articles_string, ])
            filters['codex_articles__in'] = articles
        if region and not court:
            filters['court__region'] = region
        if name == 'entried' and year:
            filters['entry_date__year'] = year
        if name == 'has_result_text':
            filters['result_text__isnull'] = True
        if name == 'resulted' and year:
            filters['result_date__year'] = year
        if name == 'resulted' and not year:
            filters['result_date__isnull'] = False
        if name == 'defendants_hidden':
            filters['defendants_hidden'] = True
        if name == 'defendants_f':
            filters['defendants__gender'] = 1
        if name == 'defendants_m':
            filters['defendants__gender'] = 2
        if name == 'defendants_na':
            filters['defendants__gender__isnull'] = True
        if name == 'penalties_all':
            filters['penalties__isnull'] = False
        if name == 'penalties_hidden':
            filters['penalties__is_hidden'] = True
        if name == 'penalties_fines_all':
            filters['penalties__type'] = 'fine'
        if name == 'penalties_fines_hidden':
            filters['penalties__type'] = 'fine'
            filters['penalties__is_hidden'] = True
        if name == 'penalties_arrests_all':
            filters['penalties__type'] = 'arrest'
        if name == 'penalties_arrests_hidden':
            filters['penalties__type'] = 'arrest'
            filters['penalties__is_hidden'] = True
        if name == 'penalties_works_all':
            filters['penalties__type'] = 'works'
        if name == 'penalties_works_hidden':
            filters['penalties__type'] = 'works'
            filters['penalties__is_hidden'] = True
        if name == 'penalties_errors':
            filters['penalties__type'] = 'error'
        # if name == 'moscow_result_text_error':
        #    filters['result_text'] = ''
        if name == 'koap1_result_was_punished':
            filters['result_type'] = 'Вынесено постановление о назначении административного наказания'
        if name == 'koap1_result_forwarded':
            filters['result_type__in'] = RESULTS_FORWARDED
        if name == 'koap1_result_cancelled':
            filters['result_type'] = 'Вынесено постановление о прекращении производства по делу об адм. правонарушении'
        if name == 'koap1_result_returned':
            filters[
                'result_type'] = 'Вынесено определение о возвращении протокола об АП и др. материалов дела в орган, ' \
                                 'долж. лицу ... в случае составления протокола и оформления других материалов дела ' \
                                 'неправомочными лицами, ...'
        return Case.objects.filter(**filters).count()

    @staticmethod
    def data_to_df(data):
        data = np.array(data)

        df = pd.DataFrame(data=data[1:, 1:],
                          index=data[1:, 0],
                          columns=data[0, 1:])
        # if format == 'png':
        df = df.astype(int)
        return df


class DataMetricsViewByYears(DataView):

    def get_data(self, request, *args, **kwargs):
        self.request = request
        years, article, regions, stage, metrics_list, type = self.process_get(request)
        region = None if not len(regions) else int(regions[0])

        data = []
        header = ['Название метрики', ] + ([x for x in years] or ['За всё время'])

        data.append(header)

        for metric in metrics_list:
            metric_arr = [all_metrics[metric], ]
            for year in years:
                m = self.get_metric(metric, article, region, year, stage, type)
                metric_arr.append(m)
            if not years:
                m = self.get_metric(metric, article, region, None, stage, type)
                metric_arr.append(m)

            data.append(metric_arr)

        return self.data_to_df(data)


class DataRegionsViewByMetrics(DataView):

    def get_data(self, request, *args, **kwargs):
        self.request = request
        years, article, regions, stage, metrics_list, type = self.process_get(request)
        year = None if not len(years) else int(years[0])
        data = []
        header = ['Регион', ] + [all_metrics[x] for x in metrics_list]
        regions_list = [x for x in dict(region_choices).keys()]
        if regions:
            regions = [int(x) for x in regions]
            regions_list = [x for x in regions_list if x in regions]

        data.append(header)

        for region in regions_list:
            region_arr = [dict(region_choices)[region], ]
            for metric in metrics_list:
                m = self.get_metric(metric, article, region, year, stage, type)
                region_arr.append(m)
            data.append(region_arr)

        return self.data_to_df(data)


class DataArticlesViewByMetrics(DataView):

    def get_data(self, request, *args, **kwargs):
        self.request = request
        years, articles, region, stage, metrics_list, type = self.process_get(request)
        year = None if not len(years) else int(years[0])
        data = []
        header = ['Статья', ] + [all_metrics[x] for x in metrics_list]

        data.append(header)
        for article in articles:
            articles_arr = [article, ]
            for metric in metrics_list:
                m = self.get_metric(metric, article, region, year, stage, type)
                articles_arr.append(m)

            data.append(articles_arr)
        return self.data_to_df(data)


class DataCourtsViewByMetrics(DataView):

    def get_data(self, request, *args, **kwargs):
        self.request = request
        years, article, regions, stage, metrics_list, type = self.process_get(request)
        year = None if not len(years) else int(years[0])
        region = None if not len(regions) else int(regions[0])
        data = []
        header = ['Суд', ] + [all_metrics[x] for x in metrics_list]
        courts = Court.objects.filter(region=region)
        data.append(header)

        for court in courts:
            court_arr = [court.title.split(' (')[0], ]
            for metric in metrics_list:
                m = self.get_metric(metric, article, region, year, stage, type, court.id)
                court_arr.append(m)
            data.append(court_arr)

        return self.data_to_df(data)
