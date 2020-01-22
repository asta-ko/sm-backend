from rest_framework import filters
from rest_framework import permissions
from rest_framework.generics import ListAPIView

from oi_sud.courts.models import Court, Judge
from oi_sud.courts.serializers import CourtSerializer, CourtShortSerializer, DebugCourtSerializer, JudgeSerializer


class CourtsDebugView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Court.objects.filter(unprocessed_cases_urls__len__gt=0).extra(
        select={'length': 'cardinality(unprocessed_cases_urls)'}).order_by('-length')
    serializer_class = DebugCourtSerializer
    filterset_fields = ['site_type', 'region']


class CourtsView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CourtSerializer
    queryset = Court.objects.all()
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)

    # search_fields = ['defendants__last_name', 'judge__name']


class CourtsSearchView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CourtShortSerializer
    queryset = Court.objects.all()
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)
    pagination_class = None


class JudgesSearchView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = JudgeSerializer
    queryset = Judge.objects.all()
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
