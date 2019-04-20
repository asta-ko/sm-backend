from django.contrib import admin

from .models import Case, KoapCase, UKCase, CaseEvent, CaseGroup, Defendant, CaseDefense

from jet.admin import CompactInline
from jet.filters import RelatedFieldAjaxListFilter

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
    list_filter = (('court', RelatedFieldAjaxListFilter), 'court__region', 'stage',  'result_type')
    list_display = ('__str__', 'court', 'judge',  'result_type', 'entry_date', 'result_date')
    search_fields = ('title', 'city', 'full_address',)
    #raw_id_fields = ('codex_articles',)

class UKCaseAdmin(CaseAdmin):
    def queryset(self, request):
        return self.model.objects.filter(type=2)

class KoapCaseAdmin(CaseAdmin):
    def queryset(self, request):
        return self.model.objects.filter(type=1)

admin.site.register(UKCase, UKCaseAdmin)
admin.site.register(KoapCase, KoapCaseAdmin)