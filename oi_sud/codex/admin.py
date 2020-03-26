from django.contrib import admin

from .models import KoapCodexArticle, UKCodexArticle


class CodexAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'short_title', 'article_number', 'codex')


admin.site.register(UKCodexArticle, CodexAdmin)
admin.site.register(KoapCodexArticle, CodexAdmin)
