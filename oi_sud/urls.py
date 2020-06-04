import datetime

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from oi_sud.cases.dataviews import (
    CountCasesView, DataCourtsViewByMetrics, DataMetricsViewByYears,
    DataRegionsViewByMetrics, FrontCountCasesView,
    )
from oi_sud.cases.views import (
    CaseView, CasesEventTypesView, CasesResultTextView, CasesResultTypesView, CasesView, SimpleCasesView,
    get_result_text,
    )
from oi_sud.codex.views import CodexArticleIListView, CodexArticleListView, CodexArticleSearchView
from oi_sud.core.admin import admin_celery_view, get_progress
from oi_sud.core.views import DebugView
from oi_sud.courts.views import CourtsDebugView, CourtsSearchView, CourtsView, JudgesSearchView
from oi_sud.users.views import CurrentUserView, LogoutView
from oi_sud.presets.views import FilterPresetViewSet, FilterPresetCategoryViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_expiring_authtoken.views import obtain_expiring_auth_token

admin.site.site_header = 'OVD-info Sud Monster'


def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

router = DefaultRouter()
router.register(r'api/v1/presets', FilterPresetViewSet, basename='preset')
router.register(r'api/v1/presetcategories', FilterPresetCategoryViewSet, basename='presetcategory')


urlpatterns = [
    path('check/', current_datetime),
    path('api/v1/users/me/', CurrentUserView.as_view(), name='current-user'),
    path('api/v1/token/', obtain_expiring_auth_token, name='token_obtain_pair'),
    path('api/v1/logout/', LogoutView.as_view()),
    path('api/v1/debug/', DebugView.as_view()),
    path('api/v1/codexarticles/', CodexArticleListView.as_view(), name='articles-list'),
    path('api/v1/codexarticles/ierarchical/', CodexArticleIListView.as_view(), name='articles-list-ierarchical'),
    path('api/v1/codexarticles/search/', CodexArticleSearchView.as_view(), name='articles-search'),
    path('api/v1/courts/', CourtsView.as_view(), name='courts-list'),
    path('api/v1/courtssearch/', CourtsSearchView.as_view(), name='courts-search'),
    path('api/v1/courtsdebug/', CourtsDebugView.as_view(), name='courts-debug-list'),
    path('api/v1/judgessearch/', JudgesSearchView.as_view(), name='judges-search'),
    path('api/v1/countcases/', CountCasesView.as_view()),
    path('api/v1/frontcountcases/', FrontCountCasesView.as_view()),
    path('api/v1/data/metrics_by_years/', DataMetricsViewByYears.as_view()),
    re_path(r'^api/v1/data/metrics_by_years/.+\.[csv|xls|xlsx|png]', DataMetricsViewByYears.as_view()),
    path('api/v1/data/regions_by_metrics/', DataRegionsViewByMetrics.as_view()),
    re_path(r'^api/v1/data/regions_by_metrics/.+\.[csv|xls|xlsx|png]', DataRegionsViewByMetrics.as_view()),
    path('api/v1/data/courts_by_metrics/', DataCourtsViewByMetrics.as_view()),
    re_path(r'^api/v1/data/courts_by_metrics/.+\.[csv|xls|xlsx|png]', DataCourtsViewByMetrics.as_view()),
    path('api/v1/casesresulttypes/', CasesResultTypesView.as_view(), name='cases-result-types'),
    path('api/v1/caseseventstypes/', CasesEventTypesView.as_view(), name='cases-events-types'),
    path('api/v1/cases/', SimpleCasesView.as_view(), name='case-list'),
    path('api/v1/casesfull/', CasesView.as_view(), name='full-case-list'),
    path('api/v1/casestexts/', CasesResultTextView.as_view(), name='case-result-list'),
    path('api/v1/cases/<int:pk>/', CaseView.as_view(), name='case-detail'),
    path('case/<int:case_id>/result.txt', get_result_text, name='case-result-text'),
    path('jet/', include('jet.urls', 'jet')),
    re_path(r'^celery_progress/(?P<task_id>[\w-]+)$', get_progress, name='task_status'),

    path('admin/active_celery_tasks/', admin_celery_view),
    path('admin/', admin.site.urls),
    ]

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
