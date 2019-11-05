from oi_sud.cases.models import Case
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def get_result_text(request, case_id):
    case = get_object_or_404(Case, pk=case_id)

    if case.result_text:
        return HttpResponse(case.result_text,  content_type='text/plain; charset=utf8')
    else:
        return HttpResponse('No result text available',  content_type='text/plain; charset=utf8')
