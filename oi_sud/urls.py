import datetime
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path
from oi_sud.core.admin import admin_celery_view, get_progress

admin.site.site_header = 'OVD-info Sud Monster'

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


urlpatterns = [
    path('', current_datetime),
    path('jet/', include('jet.urls', 'jet')),
    re_path(r'^celery_progress/(?P<task_id>[\w-]+)$', get_progress, name='task_status'),

    path('admin/active_celery_tasks/', admin_celery_view),
    path('admin/', admin.site.urls),
]

if settings.DEBUG == True:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
