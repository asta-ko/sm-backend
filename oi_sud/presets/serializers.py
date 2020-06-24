import dateparser
from django.utils import dateformat
from oi_sud.codex.models import CodexArticle
from oi_sud.core.api_utils import save_dict_or_pk_return_dict
from oi_sud.courts.models import Court, Judge
from rest_framework import serializers

from .models import FilterPreset, FilterPresetCategory


class PresetCategorySerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = FilterPresetCategory
        fields = '__all__'
        read_only_fields = ['user']


class PresetSerializer(serializers.ModelSerializer):
    category = save_dict_or_pk_return_dict(PresetCategorySerializer)  # use cautiously
    applied = serializers.SerializerMethodField()
    human_readable = serializers.SerializerMethodField()

    def validate_category(self, data):
        return data

    def get_applied(self, obj):  # hack for correct frontend rendering
        return False

    def get_human_readable(self, obj):

        # Needed for rendering tags on frontend

        params = obj.get_params.items()
        keys = obj.get_params.keys()

        final = {}
        for d in ['entry_date_range', 'result_date_range', 'event_date_range']:
            if d + "_min" in keys and d + "_max" in keys:
                date_min = dateparser.parse(obj.get_params[d + "_min"], date_formats=['%d.%m.%Y'])
                date_min_str = dateformat.format(date_min, 'd E Y')
                date_max = dateparser.parse(obj.get_params[d + "_max"], date_formats=['%d.%m.%Y'])
                date_max_str = dateformat.format(date_max, 'd E Y')
                final[d] = f"{date_min_str} — {date_max_str}"

        for k, v in params:

            if '_min' in k or '_max' in k:
                pass

            elif k == 'codex_articles':
                for article_id in v:
                    final['a-id-' + str(article_id)] = str(CodexArticle.objects.get(pk=article_id))
            elif k == 'court':
                final[k] = Court.objects.get(pk=v).title
            elif k == 'judge':
                final[k] = Judge.objects.get(pk=v).name
            else:
                final[k] = v

        return final

    def create(self, validated_data):

        if validated_data.get('category') == '':  # poor magic
            validated_data.pop('category')

        validated_data['user'] = self.context['request'].user

        return super().create(validated_data)

    class Meta:
        model = FilterPreset
        fields = '__all__'
        read_only_fields = ['user']
