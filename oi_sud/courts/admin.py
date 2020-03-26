from django.contrib import admin

from .models import Court, Judge


class CourtAdmin(admin.ModelAdmin):
    list_display = ('title', 'region', 'city', 'url', 'phone_numbers', 'full_address',)
    list_filter = ('region', 'type', 'site_type')
    search_fields = ('title', 'city', 'full_address',)


class JudgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'court')


admin.site.register(Court, CourtAdmin)
admin.site.register(Judge, JudgeAdmin)
