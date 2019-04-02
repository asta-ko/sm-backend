from django.contrib import admin

from .models import Court, Judge


class CourtAdmin(admin.ModelAdmin):

    list_display = ('title', 'region', 'city', 'url', 'type', 'site_type')
    list_filter = ('region', 'type', 'site_type')


class JudgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'court')

admin.site.register(Court, CourtAdmin)
admin.site.register(Judge, JudgeAdmin)