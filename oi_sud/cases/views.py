import itertools
import csv
import django_filters
from django.contrib.postgres.search import SearchQuery
from django.db import models
from django.db.models import Prefetch
from django.db.utils import ProgrammingError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.widgets import RangeWidget
from oi_sud.cases.models import Case, CaseEvent, PENALTY_TYPES
from oi_sud.cases.serializers import (
    CSVSerializer, CaseFullSerializer, CaseResultSerializer, CaseSerializer, SimpleCaseSerializer,
    )
from oi_sud.core.consts import region_choices
from rest_framework import filters
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.renderers import AdminRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_csv.renderers import CSVStreamingRenderer
from rest_framework_csv.misc import Echo
from django.core.paginator import Paginator
from django.http import StreamingHttpResponse


class BatchPaginator(Paginator):
    def __init__(self,*args, **kwargs):
        p_range = kwargs.pop('page_range')
        super().__init__(*args, **kwargs)
        self.p_range = p_range

    @property
    def page_range(self):
        """
        Return a 1-based range of pages for iterating through within
        a template for loop.
        """
        if self.p_range:
            return self.p_range
        return range(1, self.num_pages + 1)



class BatchCSVStreamingRenderer(CSVStreamingRenderer):

    """
    a CSV renderer that works with large querysets returning a generator
    function. Used with a streaming HTTP response, it provides response bytes
    instead of the client waiting for a long period of time
    """

    def render(self, data, renderer_context={}, *args, **kwargs):

        csv_buffer = Echo()
        csv_writer = csv.writer(csv_buffer)

        queryset = data['queryset']
        serializer = data['serializer']

        from_item = None
        to_item = None

        page_range = None


        limits = renderer_context.get('limits')
        if limits and len(limits) == 2:
            from_item = limits[0]//50 +1 or 1
            to_item = limits[1]//50
            if to_item%50:
                to_item+=1
            page_range = range(from_item, to_item)
        elif limits and len(limits) == 1:
            to_item = limits[0]//50 + 1
            if limits[0]%50:
                to_item+=1
            page_range = range(1,to_item)

        paginator = BatchPaginator(queryset, 50, page_range=page_range)

        #  rendering the header or label field was taken from the tablize
        #  method in django rest framework csv

        header = renderer_context.get('header', self.header)
        labels = renderer_context.get('labels', self.labels)

        if labels:
            yield csv_writer.writerow([labels.get(x, x) for x in header])
        if header:
            yield csv_writer.writerow(header)



        for page in paginator.page_range:

            serialized = serializer(
                paginator.page(page).object_list, many=True
            ).data

            #  we use the tablize function on the parent class to get a
            #  generator that we can use to yield a row

            table = self.tablize(
                serialized,
                header=header,
                labels=labels,
            )

            #  we want to remove the header from the tablized data so we use
            #  islice to take from 1 to the end of generator

            for row in itertools.islice(table, 1, None):
                yield csv_writer.writerow(row)

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
    # return []
    try:
        type_list = CaseEvent.objects.values_list('type', flat=True).distinct().order_by()
        type_dict = {n: n for n in type_list}
        return list(type_dict.items())
    except ProgrammingError:
        return []


class CaseFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        request = kwargs.get('request')
        if request:
            self.user = request.user
        super().__init__(*args, **kwargs)

    entry_year_from = django_filters.NumberFilter(field_name="entry_date__year", lookup_expr='gte', label="Год (от)")
    entry_year_to = django_filters.NumberFilter(field_name="entry_date__year", lookup_expr='lte', label="Год (до)")
    judge_name = django_filters.CharFilter(field_name="judge__name", lookup_expr='istartswith', label="Фамилия судьи")
    court_city = django_filters.CharFilter(field_name="court__city", lookup_expr='istartswith',
                                           label="Город/Населенный пункт")
    regions = django_filters.MultipleChoiceFilter(
        choices=region_choices,
        field_name='court__region',
        method='str_to_int',
        lookup_expr='in')
    defendant = django_filters.CharFilter(field_name="defendants__name_normalized",
                                          lookup_expr='istartswith', label="Ответчик")
    defendant_gender = django_filters.CharFilter(field_name='defendants__gender', method='filter_defendant_gender',
                                                 label='Пол ответчика')
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
    has_result = django_filters.BooleanFilter(field_name="result_type", method='filter_has_result', label="Рассмотрено")
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
    in_favorites = django_filters.BooleanFilter(field_name='in_favorites', method='filter_in_favorites',
                                                label='В избранном')

    # @property
    # def qs(self):
    #     if not hasattr(self, '_qs'):
    #         qs = self.queryset.all()
    #         if self.is_bound:
    #             # ensure form validation before filtering
    #             self.errors
    #             qs = self.filter_queryset(qs)
    #         self._qs = qs
    #     return self._qs

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

    def filter_has_result(self, queryset, name, value):
        # construct the full lookup expression.
        lookup = '__'.join([name, 'isnull'])
        return queryset.filter(**{lookup: not value})

    def filter_has_penalty(self, queryset, name, value):
        # construct the full lookup expression.
        lookup = '__'.join([name, 'isnull'])
        return queryset.filter(**{lookup: not value})

    def filter_defendant_gender(self, queryset, name, value):
        if value == 'm':
            return queryset.filter(defendants__gender='2')
        elif value == 'f':
            return queryset.filter(defendants__gender='1')
        elif value == 'na':
            return queryset.filter(defendants__gender__isnull=True)

    def str_to_int(self, queryset, name, value):
        # construct the full lookup expression.
        lookup = '__'.join([name, 'in'])
        return queryset.filter(**{lookup: [int(x) for x in value]})

    def filter_in_favorites(self, queryset, name, value):

        if self.user:
            return queryset.filter(favorited_users=self.user)
        else:
            return Case.objects.none()

    def filter_result_search(self, queryset, name, value):
        return queryset.filter(text_search=SearchQuery(value, config='russian', search_type='phrase'))

    # def get_future(self, queryset, name, value):
    #         return queryset.filter(Q(result_date__gt=timezone.now())|Q(events__isnull=True, result_date__isnull=True))

    class Meta:
        model = Case
        fields = ['stage', 'judge', 'defendants__gender']


class CaseArticleFilter(CaseFilter):
    class Meta:
        model = Case
        fields = ['stage', 'type', 'codex_articles', 'court', 'judge']


class CaseFilterBackend(DjangoFilterBackend):

    #filter_class = CaseFilter

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
                                                      queryset=CaseEvent.objects.order_by('date')), 'penalties',
                                             'defendants',
                                             'court', 'judge', 'codex_articles')

    ordering_fields = ['entry_date', 'result_date']

    @method_decorator(cache_page(60 * 60 * 1))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class CasesStreamingView(CasesView):
    renderer_classes = [BatchCSVStreamingRenderer]
    pagination_class = None
    permission_classes = ()
    paginator = None
    paginate_by = None
    paginate_by_param = None
    serializer_class = CSVSerializer
    def list(self, request, *args, **kwargs):


        queryset = self.filter_queryset(self.get_queryset())
        context = self.get_renderer_context()

        response =  StreamingHttpResponse(
            request.accepted_renderer.render({
                'queryset': queryset,
                'serializer': self.get_serializer_class(),
            }, context, content_type="text/csv"))
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        return response

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['limits'] = ([int(x) for x in self.request.GET['limits'].split(',')]
            if 'limits' in self.request.GET else None)

        context['header'] = (
            self.request.GET['fields'].split(',')
            if 'fields' in self.request.GET else None)
        return context

    #queryset = Case.objects.all()


class SimpleCasesView(CasesView):
    serializer_class = SimpleCaseSerializer
    queryset = Case.objects.prefetch_related('penalties', 'defendants', 'court', 'codex_articles')
    #
    # @method_decorator(cache_page(60*60*1))
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)


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

    @method_decorator(cache_page(60 * 60 * 24 * 2))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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

    @method_decorator(cache_page(60 * 60 * 24 * 2))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return CaseEvent.objects.distinct('type').order_by('type')

    permission_classes = (permissions.IsAdminUser,)

    # filter_backends = [CaseFilterBackend]
    # filterset_class = CaseArticleFilter

    def get(self, request, format=None):
        queryset = self.get_queryset()
        filtered = queryset.values_list('type', flat=True)
        return Response(filtered)
