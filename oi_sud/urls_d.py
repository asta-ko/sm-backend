# dummy urls for airflow
from datetime import datetime

from django.http import HttpResponse
from django.urls import path


def current_datetime(request):
    now = datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


urlpatterns = [
    path('check/', current_datetime),
]
