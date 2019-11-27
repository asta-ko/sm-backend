from rest_framework import serializers
from collections import OrderedDict
from oi_sud.courts.models import Court
from oi_sud.core.api_utils import  SkipNullValuesMixin

class DebugCourtSerializer(serializers.ModelSerializer):
    unprocessed_cases_urls_length = serializers.SerializerMethodField()
    unprocessed_cases_urls_first = serializers.SerializerMethodField()
    class Meta:
        model = Court
        fields = ['title', 'region', 'unprocessed_cases_urls_first', 'unprocessed_cases_urls_length']
        #fields = "__all__"#['order', 'title', 'duration']

    def get_unprocessed_cases_urls_length(self, obj):
        return len(obj.unprocessed_cases_urls)

    def get_unprocessed_cases_urls_first(self, obj):
        return obj.unprocessed_cases_urls[0]

class CourtSerializer(SkipNullValuesMixin, serializers.ModelSerializer):
     class Meta:
         model = Court
         fields = '__all__'




