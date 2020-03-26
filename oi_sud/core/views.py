from oi_sud.cases.models import Case
from oi_sud.courts.models import Court
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class DebugView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        data = {
            'courts_all_count': Court.objects.count(),
            'cases_all_count': Case.objects.count(),
            # 'courts_errors': Court.objects.filter(unprocessed_cases_urls__len__gt=0),
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
