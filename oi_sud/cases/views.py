import django_filters
from django.contrib.postgres.search import SearchQuery
from django.db import models
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.widgets import RangeWidget
from rest_framework import filters
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.renderers import AdminRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from oi_sud.cases.models import Case, CaseEvent, PENALTY_TYPES
from oi_sud.cases.serializers import CaseSerializer, CaseFullSerializer, CaseResultSerializer
from oi_sud.codex.models import KoapCodexArticle, UKCodexArticle


def get_result_text(request, case_id):
    case = get_object_or_404(Case, pk=case_id)

    if case.result_text:
        return HttpResponse(case.result_text, content_type='text/plain; charset=utf8')
    else:
        return HttpResponse('No result text available', content_type='text/plain; charset=utf8')


class CharArrayFilter(django_filters.BaseCSVFilter, django_filters.CharFilter):
    pass


class GroupedDateFromToRangeFilter(django_filters.DateFromToRangeFilter):
    grouped = True

    def get_lookup_and_value(self, value):
        if value:
            if value.start is not None and value.stop is not None:
                self.lookup_expr = 'range'
                value = (value.start, value.stop)
            elif value.start is not None:
                self.lookup_expr = 'gte'
                value = value.start
            elif value.stop is not None:
                self.lookup_expr = 'lte'
                value = value.stop

            return {f'{self.field_name}__{self.lookup_expr}': value}
        else:
            return {}


class GroupedChoiceFilter(django_filters.MultipleChoiceFilter):
    grouped = True

    def get_lookup_and_value(self, value):
        if value:
            return {f'{self.field_name}__{self.lookup_expr}': value}
        else:
            return {}


type_list = CaseEvent.objects.values_list('type', flat=True).distinct().order_by()
type_dict = {n: n for n in type_list}
EVENT_TYPE_CHOICES = list(type_dict.items())


class CaseFilter(django_filters.FilterSet):
    entry_year_from = django_filters.NumberFilter(field_name="entry_date__year", lookup_expr='gte', label="Год (от)")
    entry_year_to = django_filters.NumberFilter(field_name="entry_date__year", lookup_expr='lte', label="Год (до)")
    judge_name = django_filters.CharFilter(field_name="judge__name", lookup_expr='icontains', label="Фамилия судьи")
    court_city = django_filters.CharFilter(field_name="court__city", lookup_expr='icontains',
                                           label="Город/Населенный пункт")
    defendant = django_filters.CharFilter(field_name="defendants__last_name", lookup_expr='icontains', label="Ответчик")
    defendant_hidden = django_filters.BooleanFilter(field_name="defendants_hidden")
    penalty_type = django_filters.ChoiceFilter(field_name="penalties__type", choices=PENALTY_TYPES)
    penalty_hidden = django_filters.BooleanFilter(field_name="penalties__is_hidden", label="Наказание зацензурено")
    result_type = django_filters.CharFilter(field_name="result_type", lookup_expr='icontains', label="Решение по делу")
    entry_date_range = django_filters.DateFromToRangeFilter(field_name="entry_date",
                                                            widget=RangeWidget(attrs={'placeholder': 'YYYY-MM-DD'}),
                                                            label='Дата поступления')
    result_date_range = django_filters.DateFromToRangeFilter(field_name="result_date",
                                                             widget=RangeWidget(attrs={'placeholder': 'YYYY-MM-DD'}),
                                                             label='Дата поступления')
    # is_in_future = django_filters.BooleanFilter(field_name='events', method='get_future', label='Еще не рассмотрено')
    has_result_text = django_filters.BooleanFilter(field_name='result_text', method='filter_has_result_text',
                                                   label="Есть текст решения")
    result_text_search = django_filters.CharFilter(field_name="result_text", method='filter_result_search',
                                                   label="Текст решения содержит")

    event_type = GroupedChoiceFilter(field_name="events__type", choices=EVENT_TYPE_CHOICES,
                                     label="В деле есть событие этого типа")

    event_date_range = GroupedDateFromToRangeFilter(field_name="events__date",
                                                    widget=RangeWidget(attrs={'placeholder': 'YYYY-MM-DD'}),
                                                    label='И дата этого события')
    event_type_exclude = django_filters.ChoiceFilter(field_name="events__type", exclude=True,
                                                     choices=EVENT_TYPE_CHOICES,
                                                     label="В деле нет событий этого типа")

    @property
    def qs(self):
        if not hasattr(self, '_qs'):
            qs = self.queryset.all()
            if self.is_bound:
                # ensure form validation before filtering
                self.errors
                qs = self.filter_queryset(qs)
            self._qs = qs
        return self._qs

    def filter_queryset(self, queryset):
        """
        Filter the queryset with the underlying form's `cleaned_data`. You must
        call `is_valid()` or `errors` before calling this method.
        This method should be overridden if additional filtering needs to be
        applied to the queryset before it is cached.
        """
        grouped_dict = {}
        for name, value in self.form.cleaned_data.items():
            if getattr(self.filters[name], 'grouped', None):
                grouped_dict.update(self.filters[name].get_lookup_and_value(value))
            else:
                queryset = self.filters[name].filter(queryset, value)
                assert isinstance(queryset, models.QuerySet), \
                    "Expected '%s.%s' to return a QuerySet, but got a %s instead." \
                    % (type(self).__name__, name, type(queryset).__name__)

        if grouped_dict:
            queryset = queryset.filter(**grouped_dict)
        return queryset

    def filter_has_result_text(self, queryset, name, value):
        # construct the full lookup expression.
        lookup = '__'.join([name, 'isnull'])
        return queryset.filter(**{lookup: not value})

    def filter_result_search(self, queryset, name, value):
        return queryset.filter(text_search=SearchQuery(value, config='russian', search_type='phrase'))

    # def get_future(self, queryset, name, value):
    #         return queryset.filter(Q(result_date__gt=timezone.now())|Q(events__isnull=True, result_date__isnull=True))

    class Meta:
        model = Case
        fields = ['stage', 'court__region', 'judge', 'defendants__gender']


class CaseArticleFilter(CaseFilter):
    class Meta:
        model = Case
        fields = ['stage', 'type', 'court__region', 'codex_articles', 'court', 'judge']


class CaseFilterBackend(DjangoFilterBackend):

    # filter_class = CaseFilter

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

            for article_number in KoapCodexArticle.objects.filter(active=True).values_list('article_number',
                                                                                           flat=True).distinct():
                # if koap_qs.filter(codex_articles__artile_number=article_number).count():

                data['koap']['articles'][article_number] = {
                    'all': koap_qs.filter(codex_articles__article_number=article_number).count()}
                if KoapCodexArticle.objects.filter(article_number=article_number).count() > 1:
                    for article in KoapCodexArticle.objects.filter(article_number=article_number):
                        if koap_qs.filter(codex_articles__in=[article]).count():
                            data['koap']['articles'][article_number][article.__str__()] = koap_qs.filter(
                                codex_articles__in=[article]).count()
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
            return Response({'data': data})
        else:
            return Response([])


class FrontCountCasesView(APIView):

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
            # count_all = filtered_queryset.count()
            # # count_koap = filtered_queryset.filter(codex='koap')
            # data = {'all': count_all, 'koap': {'count': koap_qs.count(), 'articles': {}},
            #         'uk': {'count': uk_qs.count(), 'articles': {}}}

            data = [
                {'article': 'КОАП', 'count': koap_qs.count(), 'count_first_instance': koap_qs.filter(stage=1).count(),
                 'count_second_instance': koap_qs.filter(stage=2).count(), 'key': 'koap',
                 'description': 'Всего дел об административных правонарушениях', 'children': []},
                {'article': 'УК', 'count': uk_qs.count(), 'count_first_instance': uk_qs.filter(stage=1).count(),
                 'count_second_instance': uk_qs.filter(stage=2).count(), 'key': 'uk',
                 'description': 'Всего уголовных дел', 'children': []}]

            koap = []
            uk = []

            for article_number in KoapCodexArticle.objects.filter(active=True).values_list('article_number',
                                                                                           flat=True).distinct():
                article_qs = koap_qs.filter(codex_articles__article_number=article_number)
                main_item = {'article': article_number, 'key': article_number,
                             'count_first_instance': article_qs.filter(stage=1).count(),
                             'count_second_instance': article_qs.filter(stage=2).count(), 'count': article_qs.count(),
                             'description': KoapCodexArticle.objects.filter(
                                 article_number=article_number).first().parent_title}

                if KoapCodexArticle.objects.filter(article_number=article_number).count() > 1:
                    children = []
                    for article in KoapCodexArticle.objects.filter(article_number=article_number):
                        if koap_qs.filter(codex_articles__in=[article]).count():
                            children.append({'article': article.__str__(), 'key': article.__str__(),
                                             'count_first_instance': article_qs.filter(stage=1, codex_articles__in=[
                                                 article]).count(), 'count_second_instance': article_qs.filter(stage=2,
                                                                                                               codex_articles__in=[
                                                                                                                   article]).count(),
                                             'count': article_qs.filter(codex_articles__in=[article]).count(),
                                             'description': article.short_title})
                    if len(children):
                        main_item['children'] = children
                koap.append(main_item)
            data[0]['children'] = koap

            for article_number in UKCodexArticle.objects.filter(active=True).values_list('article_number',
                                                                                         flat=True).distinct():
                article_qs = uk_qs.filter(codex_articles__article_number=article_number)
                main_item = {'article': article_number, 'key': article_number,
                             'count_first_instance': article_qs.filter(stage=1).count(),
                             'count_second_instance': article_qs.filter(stage=2).count(),
                             'count_first_instance': article_qs.filter(stage=1, codex_articles__in=[article]).count(),
                             'count_second_instance': article_qs.filter(stage=2, codex_articles__in=[article]).count(),
                             'count': article_qs.filter(codex_articles__in=[article]).count(),
                             'description': UKCodexArticle.objects.filter(
                                 article_number=article_number).first().parent_title}

                if UKCodexArticle.objects.filter(article_number=article_number).count() > 1:
                    children = []
                    for article in UKCodexArticle.objects.filter(article_number=article_number):
                        if uk_qs.filter(codex_articles__in=[article]).count():
                            children.append({'article': article.__str__(), 'key': article.__str__(),
                                             'count_first_instance': article_qs.filter(stage=1, codex_articles__in=[
                                                 article]).count(), 'count_second_instance': article_qs.filter(stage=2,
                                                                                                               codex_articles__in=[
                                                                                                                   article]).count(),
                                             'count': article_qs.filter(codex_articles__in=[article]).count(),
                                             'description': article.short_title})
                    if len(children):
                        main_item['children'] = children
                uk.append(main_item)
            data[1]['children'] = uk

            return Response({'data': data})
        else:
            return Response({'data':[]})


class CasesView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CaseSerializer
    filter_backends = [CaseFilterBackend, filters.OrderingFilter]
    filterset_class = CaseArticleFilter
    queryset = Case.objects.prefetch_related(Prefetch('events',
                                                      queryset=CaseEvent.objects.order_by('date')), 'defendants',
                                             'court', 'judge', 'codex_articles')

    ordering_fields = ['entry_date', 'result_date']


class CaseView(RetrieveAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CaseFullSerializer
    queryset = Case.objects.prefetch_related(Prefetch('events',
                                                      queryset=CaseEvent.objects.order_by('date')), 'defendants',
                                             'court', 'judge', 'codex_articles')


class CasesResultTextView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CaseResultSerializer
    filter_backends = [CaseFilterBackend]
    filterset_class = CaseArticleFilter
    ordering_fields = ['entry_date', ]
    queryset = Case.objects.filter(result_text__isnull=False)
    renderer_classes = (AdminRenderer,)


class CasesResultTypesView(APIView):

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_queryset(self):
        return Case.objects.all()

    permission_classes = (permissions.IsAdminUser,)
    filter_backends = [CaseFilterBackend]
    filterset_class = CaseArticleFilter

    def get(self, request, format=None):
        queryset = self.get_queryset()  # Case.objects.all()
        filtered = self.filter_queryset(queryset).values_list('result_type', flat=True).distinct()
        return Response(filtered)


class CasesEventTypesView(APIView):  # TODO: may be add filtering

    # def filter_queryset(self, queryset):
    #     for backend in list(self.filter_backends):
    #         queryset = backend().filter_queryset(self.request, queryset, self)
    #     return queryset

    def get_queryset(self):
        return CaseEvent.objects.distinct('type').order_by('type')

    permission_classes = (permissions.IsAdminUser,)

    # filter_backends = [CaseFilterBackend]
    # filterset_class = CaseArticleFilter

    def get(self, request, format=None):
        queryset = self.get_queryset()
        filtered = queryset.values_list('type', flat=True)
        return Response(filtered)
