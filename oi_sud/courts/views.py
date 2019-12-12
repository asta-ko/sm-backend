from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from oi_sud.courts.models import Court
from oi_sud.courts.serializers import CourtSerializer, DebugCourtSerializer


class CourtsDebugView(ListAPIView):
    # def filter_queryset(self, queryset):
    #     for backend in list(self.filter_backends):
    #         queryset = backend().filter_queryset(self.request, queryset, self)
    #     return queryset
    # 
    # def get_queryset(self):
    #     return

    permission_classes = (permissions.IsAdminUser,)
    queryset = Court.objects.filter(unprocessed_cases_urls__len__gt=0).extra(
        select={'length': 'cardinality(unprocessed_cases_urls)'}).order_by('-length')
    serializer_class = DebugCourtSerializer
    filterset_fields = ['site_type', 'region']


class CourtsView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CourtSerializer
    queryset = Court.objects.all()

    # search_fields = ['defendants__last_name', 'judge__name']
