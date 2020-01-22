from rest_framework import filters
from rest_framework import permissions
from rest_framework.generics import ListAPIView

from oi_sud.codex.models import CodexArticle
from oi_sud.codex.serializers import CodexArticleSerializer


class CodexArticleListView(ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = CodexArticleSerializer
    queryset = CodexArticle.objects.filter(active=True)
    #filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('codex',)
    pagination_class = None
