from rest_framework import serializers

from .models import FilterPreset, FilterPresetCategory


# Serializers define the API representation.


class PresetCategorySerializer(serializers.ModelSerializer):
    # presets = PresetSerializer(many=True, read_only=True)
    class Meta:
        model = FilterPresetCategory
        fields = '__all__'


class PresetSerializer(serializers.ModelSerializer):
    category = PresetCategorySerializer()
    applied = serializers.SerializerMethodField()

    def get_applied(self, obj):  # hack for correct frontend rendering
        return False

    class Meta:
        model = FilterPreset
        fields = '__all__'
