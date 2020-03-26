from oi_sud.codex.models import CodexArticle
from rest_framework import serializers


class CodexArticleSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return str(obj)

    class Meta:
        model = CodexArticle
        fields = ['id', 'name', 'codex']
