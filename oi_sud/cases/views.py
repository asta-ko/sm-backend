import django_filters
from django.db.models import Prefetch
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.widgets import RangeWidget
from rest_framework import filters
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from oi_sud.cases.models import Case, CaseEvent
from oi_sud.cases.serializers import CaseSerializer, CaseFullSerializer
from oi_sud.codex.models import KoapCodexArticle, UKCodexArticle


def get_result_text(request, case_id):
    case = get_object_or_404(Case, pk=case_id)

    if case.result_text:
        return HttpResponse(case.result_text, content_type='text/plain; charset=utf8')
    else:
        return HttpResponse('No result text available', content_type='text/plain; charset=utf8')


class CharArrayFilter(django_filters.BaseCSVFilter, django_filters.CharFilter):
    pass


class CaseFilter(django_filters.FilterSet):

    entry_year_from = django_filters.NumberFilter(field_name="entry_date__year", lookup_expr='gte', label="Год (от)")
    entry_year_to = django_filters.NumberFilter(field_name="entry_date__year", lookup_expr='lte',label="Год (до)")
    judge = django_filters.CharFilter(field_name="judge__name", lookup_expr='icontains', label="Фамилия судьи")
    court_city = django_filters.CharFilter(field_name="court__city", lookup_expr='icontains', label="Город/Населенный пункт")
    defendant = django_filters.CharFilter(field_name="defendants__last_name", lookup_expr='icontains', label="Ответчик")
    result_type =  django_filters.CharFilter(field_name="result_type", lookup_expr='icontains', label="Решение по делу")
    result_text_contains = django_filters.CharFilter(field_name="result_text", lookup_expr='icontains', label="Текст решения содержит")
    date_range = django_filters.DateFromToRangeFilter(field_name="entry_date", widget=RangeWidget(attrs={'placeholder': 'YYYY-MM-DD'}))
    #is_in_future = django_filters.BooleanFilter(field_name='events', method='get_future', label='Еще не рассмотрено')
    has_result_text = django_filters.BooleanFilter(field_name='result_text', method='filter_result_text')

    def filter_result_text(self, queryset, name, value):
        # construct the full lookup expression.
        return queryset.filter(result_text__isnull=False)
    # def get_future(self, queryset, name, value):
    #         return queryset.filter(Q(result_date__gt=timezone.now())|Q(events__isnull=True, result_date__isnull=True))


    class Meta:
        model = Case
        fields = ['stage','court__region', 'defendants__gender']

class CaseArticleFilter(CaseFilter):

    class Meta:
        model = Case
        fields = ['stage','type','court__region', 'codex_articles']

class CaseFilterBackend(DjangoFilterBackend):

    #filter_class = CaseFilter

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)

        if filter_class:
            return filter_class(request.query_params, queryset=queryset, request=request).qs
        return queryset


class CountCasesView(APIView):

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_queryset(self):
        return Case.objects.all()

    permission_classes = (permissions.IsAdminUser,)
    filter_backends = [CaseFilterBackend]
    filterset_class = CaseFilter

    def get(self, request, format=None):
        queryset = self.get_queryset()  # Case.objects.all()
        filtered_queryset = self.filter_queryset(queryset)

        koap_qs = filtered_queryset.filter(type=1)
        uk_qs = filtered_queryset.filter(type=2)

        if filtered_queryset.exists():
            count_all = filtered_queryset.count()
            # count_koap = filtered_queryset.filter(codex='koap')
            data = {'all': count_all, 'koap': {'count': koap_qs.count(), 'articles': {}},
                    'uk': {'count': uk_qs.count(), 'articles': {}}}

            for article_number in KoapCodexArticle.objects.filter(active=True).values_list('article_number', flat=True).distinct():
                #if koap_qs.filter(codex_articles__artile_number=article_number).count():

                data['koap']['articles'][article_number] = {'all':koap_qs.filter(codex_articles__article_number=article_number).count()}
                if KoapCodexArticle.objects.filter(article_number=article_number).count() > 1:
                    for article in KoapCodexArticle.objects.filter(article_number=article_number):
                        if koap_qs.filter(codex_articles__in=[article]).count():
                            data['koap']['articles'][article_number][article.__str__()] = koap_qs.filter(codex_articles__in=[article]).count()
            for article_number in UKCodexArticle.objects.filter(active=True).values_list('article_number',
                                                                                           flat=True).distinct():
                # if koap_qs.filter(codex_articles__artile_number=article_number).count():
                data['uk']['articles'][article_number] = {
                    'all': uk_qs.filter(codex_articles__article_number=article_number).count()}
                if UKCodexArticle.objects.filter(article_number=article_number).count() > 1:
                    for article in UKCodexArticle.objects.filter(article_number=article_number):
                        if uk_qs.filter(codex_articles__in=[article]).count():
                            data['uk']['articles'][article_number][article.__str__()] = uk_qs.filter(
                                codex_articles__in=[article]).count()

            # for article in UKCodexArticle.objects.filter(active=True):
            #     if uk_qs.filter(codex_articles__in=[article]).count():
            #         data['uk']['articles'][article.__str__()] = uk_qs.filter(codex_articles__in=[article]).count()
            return Response([data])
        else:
            return Response([])

class CasesView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CaseSerializer
    filter_backends = [CaseFilterBackend, filters.OrderingFilter]
    filterset_class = CaseArticleFilter
    queryset = Case.objects.prefetch_related(Prefetch('events',
        queryset=CaseEvent.objects.order_by('date')), 'defendants', 'court', 'judge', 'codex_articles')

    # search_fields = ['defendants__last_name', 'judge__name']
    ordering_fields = ['entry_date',]


class CaseView(RetrieveAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CaseFullSerializer
    queryset = Case.objects.prefetch_related(Prefetch('events',
        queryset=CaseEvent.objects.order_by('date')), 'defendants', 'court', 'judge', 'codex_articles')

