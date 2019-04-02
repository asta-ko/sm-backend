from django.contrib import admin

from .models import CodexArticle


class CodexAdmin(admin.ModelAdmin):
    list_filter = ('codex',)
    list_display = ('__str__', 'short_title', 'article_number', 'codex')


admin.site.register(CodexArticle, CodexAdmin)
