from oi_sud.cases.models import Case, CaseEvent, CasePenalty, Defendant
from oi_sud.core.api_utils import SkipNullValuesMixin
from rest_framework import serializers
from reversion.models import Version


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


class PenaltySerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    human_readable = serializers.SerializerMethodField()

    def get_human_readable(self, obj):
        return str(obj)

    class Meta:
        model = CasePenalty
        exclude = ['id', 'case', 'defendant']


class CaseSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    in_favorites = serializers.SerializerMethodField()
    judge = serializers.SerializerMethodField()
    court = serializers.SerializerMethodField()
    codex_articles = serializers.SerializerMethodField()
    revisions = serializers.SerializerMethodField()
    defendants = DefendantSerializer(many=True, read_only=True)
    defendants_simple = serializers.SerializerMethodField()
    events = CaseEventSerializer(many=True, read_only=True)
    stage = serializers.CharField(source='get_stage_display')
    type = serializers.CharField(source='get_type_display')
    admin_url = serializers.SerializerMethodField()
    api_url = serializers.HyperlinkedIdentityField(view_name='case-detail')
    result_text_url = serializers.SerializerMethodField()
    penalties = PenaltySerializer(many=True, read_only=True)
    linked_cases = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='case-detail'
        )

    def get_in_favorites(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if request.user in obj.favorited_users.all():
                return True
            return False

    def get_defendants_simple(self, obj):
        if obj.defendants.count():
            try:
                return ', '.join(list([x.name_normalized for x in obj.defendants.all()]))
            except TypeError:
                return ''

    class Meta:
        model = Case
        exclude = ['result_text', 'advocates', 'text_search']

    def get_penalty(self, obj):
        if obj.penalties.first():
            return obj.penalties.all().first()
        else:
            return None

    def get_judge(self, obj):
        return str(obj.judge)

    def get_court(self, obj):
        return str(obj.court)

    def get_codex_articles(self, obj):
        return [str(x) for x in obj.codex_articles.all()]

    def get_revisions(self, obj):
        revisions = Version.objects.get_for_object(obj)
        if len(revisions) > 1:
            return {
                'link': obj.get_history_link(),
                'revisions': [{'date': str(x.revision.date_created), 'comment': x.revision.comment} for x in
                              Version.objects.get_for_object(obj)]
                }

    def get_defendants(self, obj):
        if obj.defendants_hidden:
            return 'hidden'
        return [str(x) for x in obj.defendants.all()]

    def get_admin_url(self, obj):
        return obj.get_admin_url()

    def get_result_text_url(self, obj):
        if obj.result_text:
            return obj.get_result_text_url()


class SimpleCaseSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    in_favorites = serializers.SerializerMethodField()
    court = serializers.SerializerMethodField()
    codex_articles = serializers.SerializerMethodField()
    defendants_simple = serializers.SerializerMethodField()
    result_text_url = serializers.SerializerMethodField()
    penalties = PenaltySerializer(many=True, read_only=True)

    def get_in_favorites(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if request.user in obj.favorited_users.all():
                return True
            return False

    def get_defendants_simple(self, obj):
        if obj.defendants.count():
            try:
                return ', '.join(list([x.name_normalized for x in obj.defendants.all()]))
            except TypeError:
                return ''

    class Meta:
        model = Case
        fields = ['id','entry_date','result_date','in_favorites','court','codex_articles','defendants_simple','penalties','result_text_url']

    def get_penalty(self, obj):
        if obj.penalties.first():
            return obj.penalties.all().first()
        else:
            return None

    def get_court(self, obj):
        return str(obj.court)

    def get_codex_articles(self, obj):
        return [str(x) for x in obj.codex_articles.all()]

    def get_defendants(self, obj):
        if obj.defendants_hidden:
            return 'hidden'
        return [str(x) for x in obj.defendants.all()]

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
