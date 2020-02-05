from rest_framework import serializers

from oi_sud.codex.models import CodexArticle


class CodexArticleSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return str(obj)

    class Meta:
        model = CodexArticle
        fields = ['id', 'name', 'codex']
