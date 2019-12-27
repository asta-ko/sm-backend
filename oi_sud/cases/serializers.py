from rest_framework import serializers
from reversion.models import Version

from oi_sud.cases.models import Case, CaseEvent, Defendant
from oi_sud.core.api_utils import SkipNullValuesMixin


class CaseEventSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    class Meta:
        model = CaseEvent
        exclude = ['case', 'id', 'created_at']
        # fields = "__all__"#['order', 'title', 'duration']


class DefendantSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    gender = serializers.CharField(source='get_gender_display')

    class Meta:
        model = Defendant
        exclude = ['id', 'region', 'created_at']


class CaseSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    judge = serializers.SerializerMethodField()
    court = serializers.SerializerMethodField()
    codex_articles = serializers.SerializerMethodField()
    revisions = serializers.SerializerMethodField()
    defendants = DefendantSerializer(many=True, read_only=True)
    events = CaseEventSerializer(many=True, read_only=True)
    stage = serializers.CharField(source='get_stage_display')
    type = serializers.CharField(source='get_type_display')
    admin_url = serializers.SerializerMethodField()
    api_url = serializers.HyperlinkedIdentityField(view_name='case-detail')
    result_text_url = serializers.SerializerMethodField()
    linked_cases = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='case-detail'
    )

    class Meta:
        model = Case
        exclude = ['result_text', 'advocates', 'text_search']

    def get_judge(self, obj):
        return str(obj.judge)

    def get_court(self, obj):
        return str(obj.court)

    def get_codex_articles(self, obj):
        return [str(x) for x in obj.codex_articles.all()]

    def get_revisions(self, obj):
        revisions = Version.objects.get_for_object(obj)
        if len(revisions) > 1:
            return {'link': obj.get_history_link(),
                    'revisions': [{'date': str(x.revision.date_created), 'comment': x.revision.comment} for x in
                                  Version.objects.get_for_object(obj)]}

    def get_defendants(self, obj):
        if obj.defendants_hidden:
            return 'hidden'
        return [str(x) for x in obj.defendants.all()]

    def get_admin_url(self, obj):
        return obj.get_admin_url()

    def get_result_text_url(self, obj):
        if obj.result_text:
            return obj.get_result_text_url()


class CaseFullSerializer(CaseSerializer):
    class Meta:
        model = Case
        exclude = ['advocates']


class CaseResultSerializer(serializers.ModelSerializer):
    codex_articles = serializers.SerializerMethodField()
    result_text_url = serializers.SerializerMethodField()
    api_url = serializers.HyperlinkedIdentityField(view_name='case-detail')

    def get_codex_articles(self, obj):
        return [str(x) for x in obj.codex_articles.all()]

    def get_result_text_url(self, obj):
        if obj.result_text:
            return obj.get_result_text_url()

    class Meta:
        model = Case
        fields = ['result_text_url', 'url', 'api_url', 'codex_articles']
