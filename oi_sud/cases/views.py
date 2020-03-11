import django_filters
from django.contrib.postgres.search import SearchQuery
from django.db import models
from django.db.models import Prefetch
from django.db.utils import ProgrammingError
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


def get_event_type_choices():
    #return []
    try:
        type_list = CaseEvent.objects.values_list('type', flat=True).distinct().order_by()
        type_dict = {n: n for n in type_list}
        return list(type_dict.items())
    except ProgrammingError:
        return []

class CaseFilter(django_filters.FilterSet):

    entry_year_from = django_filters.NumberFilter(field_name="entry_date__year", lookup_expr='gte', label="Год (от)")
    entry_year_to = django_filters.NumberFilter(field_name="entry_date__year", lookup_expr='lte', label="Год (до)")
    judge_name = django_filters.CharFilter(field_name="judge__name", lookup_expr='icontains', label="Фамилия судьи")
    court_city = django_filters.CharFilter(field_name="court__city", lookup_expr='icontains',
                                           label="Город/Населенный пункт")
    defendant = django_filters.CharFilter(field_name="defendants__last_name", lookup_expr='icontains', label="Ответчик")
    defendant_hidden = django_filters.BooleanFilter(field_name="defendants_hidden")
    penalty_type = django_filters.ChoiceFilter(field_name="penalties__type", choices=PENALTY_TYPES)
    has_penalty = django_filters.BooleanFilter(field_name="penalties", method='filter_has_penalty',
                                               label="Нет наказания")
    penalty_hidden = django_filters.BooleanFilter(field_name="penalties__is_hidden", label="Наказание зацензурено")
    penalty_from = django_filters.NumberFilter(field_name="penalties__num", lookup_expr="gte",
                                               label="Размер наказания (от)")
    penalty_to = django_filters.NumberFilter(field_name="penalties__num", lookup_expr="lte",
                                             label="Размер наказания (до)")
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

    event_type = GroupedChoiceFilter(field_name="events__type", choices=get_event_type_choices(),
                                     label="В деле есть событие этого типа")

    event_date_range = GroupedDateFromToRangeFilter(field_name="events__date",
                                                    widget=RangeWidget(attrs={'placeholder': 'YYYY-MM-DD'}),
                                                    label='И дата этого события')
    event_type_exclude = django_filters.ChoiceFilter(field_name="events__type", exclude=True,
                                                     choices=get_event_type_choices(),
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

    def filter_has_penalty(self, queryset, name, value):
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
