import django_filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from oi_sud.core.consts import region_choices
from oi_sud.courts.models import Court, Judge
from oi_sud.courts.serializers import CitySerializer, CourtSerializer, CourtShortSerializer, DebugCourtSerializer, \
    JudgeSerializer
from rest_framework import filters
from rest_framework import permissions
from rest_framework.generics import ListAPIView


class CourtsDebugView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Court.objects.filter(unprocessed_cases_urls__len__gt=0).extra(
        select={'length': 'cardinality(unprocessed_cases_urls)'}).order_by('-length')
    serializer_class = DebugCourtSerializer
    filterset_fields = ['site_type', 'region']


class RegionsFilter(django_filters.FilterSet):
    region_fieldname = None

    allowed_regions = django_filters.MultipleChoiceFilter(
        choices=region_choices,
        field_name=region_fieldname,
        method='str_to_int',
        lookup_expr='in')

    def str_to_int(self, queryset, name, value):
        # construct the full lookup expression.
        lookup = '__'.join([self.region_fieldname, 'in'])
        return queryset.filter(**{lookup: [int(x) for x in value]})


class CourtFilter(RegionsFilter):
    region_fieldname = 'region'

    class Meta:
        model = Court
        fields = ['city', 'title']


class JudgeFilter(RegionsFilter):
    region_fieldname = 'court__region'

    class Meta:
        model = Judge
        fields = ['name', 'court__region', 'court']


class CourtsView(ListAPIView):

    @method_decorator(cache_page(60 * 60 * 24 * 30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CourtSerializer
    queryset = Court.objects.all()
    search_fields = ['title']
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    # filter_fields = ('city')
    filter_class = CourtFilter
    # search_fields = ['defendants__last_name', 'judge__name']


class CourtsSearchView(ListAPIView):

    @method_decorator(cache_page(60 * 60 * 24 * 30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CourtShortSerializer
    queryset = Court.objects.all()
    search_fields = ['title']
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filter_class = CourtFilter
    filter_fields = ('region', 'city')
    pagination_class = None


class CitiesSearchView(ListAPIView):

    @method_decorator(cache_page(60 * 60 * 24 * 30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CitySerializer
    queryset = Court.objects.all().distinct('city')
    search_fields = ['city']
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filter_class = CourtFilter
    filter_fields = ('region',)
    pagination_class = None


class JudgesSearchView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = JudgeSerializer
    queryset = Judge.objects.all()
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
