from django.contrib import admin

from .models import Case, CaseEvent, CaseGroup, Defendant, CaseDefense

from jet.admin import CompactInline

class DefendantsInline(CompactInline):
    model = CaseDefense
    show_change_link = True
    extra = 0

class CaseEventsInline(CompactInline):
    model = CaseEvent
    show_change_link = True
    extra = 0

class CaseAdmin(admin.ModelAdmin):
    inlines = (DefendantsInline, CaseEventsInline)
    list_filter = ('court', 'court__region', 'stage', 'type', 'result_type')
    list_display = ('__str__', 'court', 'judge', 'entry_date', 'result_date', 'result_type' )
    search_fields = ('title', 'city', 'full_address',)
    #raw_id_fields = ('codex_articles',)

admin.site.register(Case, CaseAdmin)
