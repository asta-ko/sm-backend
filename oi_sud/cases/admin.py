from django.contrib import admin
from django.utils.html import format_html
from django.forms.utils import flatatt
from django.contrib.admin.utils import get_model_from_relation
from django.urls import reverse
from django.utils.encoding import smart_text
from .models import Case, KoapCase, UKCase, CaseEvent, CaseGroup, Defendant, CaseDefense
from jet.admin import CompactInline
from jet.filters import RelatedFieldAjaxListFilter

class ArticlesRelatedFieldAjaxListFilter(RelatedFieldAjaxListFilter):

    def field_choices(self, field, request, model_admin):
        # Very dirty hack
        model = field.remote_field.model if hasattr(field, 'remote_field') else field.related_field.model
        app_label = model._meta.app_label

        if model_admin.__class__.__name__ == 'KoapCaseAdmin':
            model_name = 'KoapCodexArticle'
        elif model_admin.__class__.__name__ == 'UKCaseAdmin':
            model_name = 'UKCodexArticle'
        self.ajax_attrs = format_html('{0}', flatatt({
            'data-app-label': app_label,
            'data-model': model_name,
            'data-ajax--url': reverse('jet:model_lookup'),
            'data-queryset--lookup': self.lookup_kwarg,
        }))

        if self.lookup_val is None:
            return []
        other_model = get_model_from_relation(field)
        if hasattr(field, 'rel'):
            rel_name = field.rel.get_related_field().name
        else:
            rel_name = other_model._meta.pk.name
        queryset = model._default_manager.filter(**{rel_name: self.lookup_val}).all()
        return [(x._get_pk_val(), smart_text(x)) for x in queryset]


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
    list_filter = (('codex_articles',ArticlesRelatedFieldAjaxListFilter), ('court', RelatedFieldAjaxListFilter), 'court__region', 'stage',  'result_type')
    list_display = ('__str__', 'court', 'judge',  'result_type', 'entry_date', 'result_date')
    search_fields = ('case_number', 'protocol_number', 'result_text')

class DefendantAdmin(admin.ModelAdmin):
    pass

class UKCaseAdmin(CaseAdmin):
    def queryset(self, request):
        return self.model.objects.filter(type=2)

class KoapCaseAdmin(CaseAdmin):
    def queryset(self, request):
        return self.model.objects.filter(type=1)


admin.site.register(UKCase, UKCaseAdmin)
admin.site.register(KoapCase, KoapCaseAdmin)
admin.site.register(Defendant, DefendantAdmin)