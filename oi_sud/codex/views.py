from collections import OrderedDict

from oi_sud.codex.models import CodexArticle
from oi_sud.codex.serializers import CodexArticleSerializer
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class CodexArticleListView(ListAPIView):

    @method_decorator(cache_page(60 * 60 * 24 * 10))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CodexArticleSerializer
    queryset = CodexArticle.objects.filter(active=True)
    # filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('codex',)
    pagination_class = None


class CodexArticleIListView(APIView):
    queryset = CodexArticle.objects.filter(active=True)

    @method_decorator(cache_page(60 * 60 * 24 * 10))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, format=None):
        data = OrderedDict()
        queryset = self.queryset
        if request.GET.get('codex'):
            queryset = queryset.filter(codex=request.GET.get('codex'))

        for article_number in queryset.values_list('article_number', flat=True).distinct():
            if queryset.filter(article_number=article_number).count() > 1:
                main_name = f'{article_number}'
                data[main_name] = f'ст. {main_name} (вся)'
                for a in queryset.filter(article_number=article_number):
                    data[a.get_number_and_part()] = f'ст. {str(a)}'
            else:
                a = queryset.filter(article_number=article_number).first()
                data[a.get_number_and_part()] = f'ст. {str(a)}'

        return Response(data)


class CodexArticleSearchView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CodexArticleSerializer
    queryset = CodexArticle.objects.all()
    search_fields = ['article_number']
    filter_fields = ('codex')
    pagination_class = None

    @method_decorator(cache_page(60 * 60 * 24 * 10))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
