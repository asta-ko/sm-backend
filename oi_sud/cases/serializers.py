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
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return ' '.join([x for x in [obj.last_name, obj.first_name, obj.middle_name] if x is not None])

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


class LinkedCaseSerializer(serializers.ModelSerializer):
    case_title = serializers.SerializerMethodField()

    def get_case_title(self, obj):
        return f'{obj.stage} инстанция: {obj.case_number} {obj.court}'

    class Meta:
        model = Case
        fields = ['id', 'stage', 'case_title']


class BaseCaseSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    in_favorites = serializers.SerializerMethodField()
    judge = serializers.SerializerMethodField()
    court = serializers.SerializerMethodField()
    codex_articles = serializers.SerializerMethodField()
    revisions = serializers.SerializerMethodField()
    defendants = DefendantSerializer(many=True, read_only=True)
    defendants_simple = serializers.SerializerMethodField()
    advocates = serializers.SerializerMethodField()
    prosecutors = serializers.SerializerMethodField()
    events = CaseEventSerializer(many=True, read_only=True)
    stage = serializers.CharField(source='get_stage_display')
    type = serializers.CharField(source='get_type_display')
    admin_url = serializers.SerializerMethodField()
    api_url = serializers.HyperlinkedIdentityField(view_name='case-detail')
    result_text_url = serializers.SerializerMethodField()
    penalties = PenaltySerializer(many=True, read_only=True)
    penalty = serializers.SerializerMethodField()
    linked_cases = LinkedCaseSerializer(
        many=True,
        read_only=True
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

    def get_advocates(self, obj):
        try:
            return ', '.join(list([x.name_normalized for x in obj.get_advocates()]))
        except TypeError:
            return ''

    def get_prosecutors(self, obj):
        try:
            return ', '.join(list([x.name_normalized for x in obj.get_prosecutors()]))
        except TypeError:
            return ''

    class Meta:
        model = Case
        exclude = ['result_text', 'text_search']

    def get_penalty(self, obj):
        if obj.penalties.first():
            return str(obj.penalties.all().first())
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


class CaseSerializer(BaseCaseSerializer, SkipNullValuesMixin):
    pass


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
        fields = ['id', 'entry_date', 'result_date', 'in_favorites', 'court', 'codex_articles', 'defendants_simple',
                  'penalties', 'result_type', 'result_text_url']

    def get_penalty(self, obj):
        if obj.penalties.first():
            return obj.penalties.all().first()
        else:
            return None

    def get_court(self, obj):
        return str(obj.court)

    def get_codex_articles(self, obj):
        return ', '.join([str(x) for x in obj.codex_articles.all()])

    def get_defendants(self, obj):
        if obj.defendants_hidden:
            return 'hidden'
        return [str(x) for x in obj.defendants.all()]

    def get_result_text_url(self, obj):
        if obj.result_text:
            return obj.get_result_text_url()


class CSVSerializer(SimpleCaseSerializer):
    court_city = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    defendants_gender = serializers.SerializerMethodField()
    penalty = serializers.SerializerMethodField()
    penalty_type = serializers.SerializerMethodField()
    penalty_value = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = ['id', 'entry_date', 'result_date', 'in_favorites', 'court', 'codex_articles', 'defendants_simple',
                  'penalty', 'penalty_type', 'penalty_value', 'result_type', 'result_text_url', 'court_city', 'region',
                  'type', 'stage', 'url', 'appeal_date', 'defendants_gender', 'judge',
                  ]

    def get_penalty_type(self, obj):
        return obj.penalties.first().get_type_display() if obj.penalties.exists() else None

    def get_penalty_value(self, obj):
        return obj.penalties.first().num if obj.penalties.all().exists() else None

    def get_judge(self, obj):
        return str(self.obj.judge)

    def get_defendants_gender(self, obj):
        return ', '.join([x.get_gender_display() or '-' for x in obj.defendants.all()])

    def get_court_city(self, obj):
        return obj.court.city

    def get_region(self, obj):
        return obj.court.region

    def get_penalty(self, obj):
        if obj.penalties.first():
            return obj.penalties.all().first()
        else:
            return None


class CaseFullSerializer(CaseSerializer):
    pass


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
