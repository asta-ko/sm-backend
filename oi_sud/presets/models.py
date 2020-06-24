from django.contrib.postgres.fields import JSONField
from django.db import models
from oi_sud.core.utils import nullable


class FilterPresetCategory(models.Model):
    title = models.CharField(max_length=75, blank=False, null=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='preset_categories')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'title'], name='unique_preset_category')]

    def __str__(self):
        return self.title


class FilterPreset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', **nullable)
    title = models.CharField(max_length=75, null=True, blank=False)
    description = models.TextField(**nullable)
    get_params = JSONField(null=False, blank=False)
    category = models.ForeignKey(FilterPresetCategory, on_delete=models.SET_NULL, related_name='presets', **nullable)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='presets')

    def __str__(self):
        return self.title

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'title'], name='unique_preset')]
