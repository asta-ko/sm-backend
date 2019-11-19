from rest_framework import serializers
from collections import OrderedDict
from oi_sud.cases.models import Case, CaseEvent, Defendant
from rest_framework.relations import PKOnlyObject
#from rest_framework.reverse import reverse
from django.urls import reverse


class SkipNullValuesMixin(object):
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # KEY IS HERE:
            if attribute in [None, '']:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

class CaseEventSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    class Meta:
        model = CaseEvent
        exclude = ['case', 'id', 'created_at']
        #fields = "__all__"#['order', 'title', 'duration']


class DefendantSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    gender = serializers.CharField(source='get_gender_display')
    class Meta:
        model = Defendant
        exclude = ['id', 'region', 'created_at']

class CaseSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
    judge = serializers.SerializerMethodField()
    court = serializers.SerializerMethodField()
    codex_articles = serializers.SerializerMethodField()
    defendants =  DefendantSerializer(many=True, read_only=True)
    events = CaseEventSerializer(many=True, read_only=True)
    stage = serializers.CharField(source='get_stage_display')
    type = serializers.CharField(source='get_type_display')
    admin_url = serializers.SerializerMethodField()
    api_url = serializers.HyperlinkedIdentityField(view_name='case-detail')
    result_text_url =  serializers.SerializerMethodField()
    linked_cases = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='case-detail'
    )

    class Meta:
        model = Case
        exclude = ['result_text',  'advocates']

    def get_judge(self, obj):
        return str(obj.judge)

    def get_court(self,obj):
        return str(obj.court)

    def get_codex_articles(self, obj):
        return [str(x) for x in obj.codex_articles.all()]

    def get_defendants(self,obj):
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



