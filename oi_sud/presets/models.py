from django.contrib.postgres.fields import JSONField
from django.db import models
from oi_sud.core.utils import nullable


class FilterPresetCategory(models.Model):
    title = models.CharField(max_length=75, blank=False, null=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='preset_categories')


class FilterPreset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', **nullable)
    title = models.CharField(max_length=75, **nullable)
    description = models.TextField(**nullable)
    get_params = JSONField(null=True, blank=False)
    human_readable = JSONField(null=True, blank=False)
    category = models.ForeignKey(FilterPresetCategory, on_delete=models.SET_NULL, related_name='presets', **nullable)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='presets')
