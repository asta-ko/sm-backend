import datetime
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path

from oi_sud.core.admin import admin_celery_view, get_progress
<<<<<<< Updated upstream
from oi_sud.cases.views import get_result_text, CountCasesView, CasesResultTextView, CasesView, CaseView
=======
from oi_sud.cases.views import get_result_text, CountCasesView, CasesView, CaseView, CasesResultTextView
>>>>>>> Stashed changes
from oi_sud.courts.views import CourtsView, CourtsDebugView

admin.site.site_header = 'OVD-info Sud Monster'


def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


urlpatterns = [
    path('', current_datetime),
    path('api/v1/courts', CourtsView.as_view(), name='courts-list'),
    path('api/v1/courtsdebug', CourtsDebugView.as_view(), name='courts-debug-list'),
    path('api/v1/countcases', CountCasesView.as_view()),
    path('api/v1/cases', CasesView.as_view(), name='case-list'),
    path('api/v1/casestexts', CasesResultTextView.as_view(), name='case-result-list'),
    path('api/v1/cases/<int:pk>', CaseView.as_view(), name='case-detail'),
    path('case/<int:case_id>/result.txt', get_result_text, name='case-result-text'),
    path('jet/', include('jet.urls', 'jet')),
    re_path(r'^celery_progress/(?P<task_id>[\w-]+)$', get_progress, name='task_status'),

    path('admin/active_celery_tasks/', admin_celery_view),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
