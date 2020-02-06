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
from oi_sud.courts.models import Court


class DebugView(APIView):

    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        data = {
        'courts_all_count': Court.objects.count(),
        'cases_all_count': Case.objects.count(),
        #'courts_errors': Court.objects.filter(unprocessed_cases_urls__len__gt=0),
        'courts_errors_count': Court.objects.filter(unprocessed_cases_urls__len__gt=0).count(),
        'cases_first_instance': Case.objects.filter(stage=1).count(),
        'cases_second_instance': Case.objects.filter(stage=2).count(),
        'cases_without_first_instance': Case.objects.filter(stage=2, linked_cases__isnull=True).count(),
        'cases_without_defendants': Case.objects.filter(defendants__isnull=True, defendants_hidden=False).count(),
        'cases_without_articles': Case.objects.filter(codex_articles__isnull=True).count(),
        'cases_without_events': Case.objects.filter(events__isnull=True).count()
        }
        return Response({'data': data})


#
#
# class CourtsDebugView(ListAPIView):
#     permission_classes = (permissions.IsAdminUser,)
#     queryset = Court.objects.filter(unprocessed_cases_urls__len__gt=0).extra(
#         select={'length': 'cardinality(unprocessed_cases_urls)'}).order_by('-length')
#     serializer_class = DebugCourtSerializer
#     filterset_fields = ['site_type', 'region']