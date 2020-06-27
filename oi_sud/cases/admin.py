from django.contrib import admin
from django.contrib.admin.utils import get_model_from_relation
from django.forms.utils import flatatt
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.html import format_html
from jet.admin import CompactInline
from jet.filters import RelatedFieldAjaxListFilter
from reversion_compare.admin import CompareVersionAdmin

from .models import Case, CaseDefense, CaseEvent, Defendant, KoapCase, LinkedCasesProxy, UKCase


class ArticlesRelatedFieldAjaxListFilter(RelatedFieldAjaxListFilter):

    def field_choices(self, field, request, model_admin):
        # Very dirty hack
        model = field.remote_field.model if hasattr(field, 'remote_field') else field.related_field.model
        app_label = model._meta.app_label

        model_name = None

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

class CaseInline(CompactInline):
    model = Case
    show_change_link = True
    extra = 0


class LinkedCases(CompactInline):
    model = LinkedCasesProxy
    fk_name = 'from_case'
    verbose_name = "Связанное дело"
    verbose_name_plural = "Связанные дела"
    extra = 0
    readonly_fields = ('admin_link',)
    exclude = ['to_case']

    def admin_link(self, instance):
        return format_html(
            f'<a href="/admin/cases/{instance.get_codex_type()}case/{instance.get_pk()}/change/">Link</a>')


class CaseAdmin(CompareVersionAdmin, admin.ModelAdmin):
    inlines = (DefendantsInline, CaseEventsInline, LinkedCases)
    list_filter = (('codex_articles', ArticlesRelatedFieldAjaxListFilter), ('court', RelatedFieldAjaxListFilter),
                   ('judge', RelatedFieldAjaxListFilter), 'court__region', 'stage',)
    list_display = (
        '__str__', 'judge', 'result_type', 'entry_date', 'result_date', 'has_result_text_icon', 'has_linked_cases')
    search_fields = ('case_number', 'protocol_number', 'result_text')

    def has_linked_cases(self, obj):
        if obj.get_2_instance_case():
            second_instance_case = obj.get_2_instance_case()
            link = f'/admin/cases/{second_instance_case.get_codex_type()}case/{second_instance_case.pk}/change/'
            return format_html(f'<a href="{link}">2 инстанция</a>')
        if obj.get_1_instance_case():
            first_instance_case = obj.get_1_instance_case()
            link = f'/admin/cases/{first_instance_case.get_codex_type()}case/{first_instance_case.pk}/change/'
            return format_html(f'<a href="{link}">1 инстанция</a>')

    has_linked_cases.short_description = 'Связанные дела'

    def has_result_text_icon(self, obj):
        if obj.result_text:
            return format_html(
                f'<a href="{obj.get_result_text_url()}" download><i class="fas fa-file-alt"></i></a>')

    has_result_text_icon.short_description = 'Есть текст'

    def get_form(self, request, obj=None, **kwargs):
        exclude = ['text_search', ]
        for field in Case._meta.get_fields():
            if field.name in ['caseevent', 'casedefense', ]:
                continue
            if getattr(obj, field.name) is None:
                exclude.append(field.name)
        self.exclude = tuple(exclude)
        form = super(CaseAdmin, self).get_form(request, obj, **kwargs)
        return form

    class Media:
        css = {
            'all': ('https://use.fontawesome.com/releases/v5.8.2/css/all.css',)
            }


class DefendantAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('name_normalized',)
    list_filter = ('risk_group',)


    fields = ('created_at','region','gender','name_normalized','first_name','middle_name','last_name','list_cases')
    readonly_fields = ('created_at','list_cases')

    def list_cases(self, obj):
        html = '<br><br><hr style="width:300px">'
        for case in obj.cases.exclude(duplicate=True):
            articles_list = ','.join([str(x) for x in case.codex_articles.all()])
            c_text = f'{case.result_date} {articles_list} {case.stage}'
            html += f'⯈ <a style="line-height:40px" href="{case.get_admin_url()}">{c_text}</a><hr ' \
                    f'style="width:300px">'
        return format_html(html)


    list_cases.allow_tags = True


    def get_case_court(self, obj):
        if obj.cases.first():
            return obj.cases.first().court

    def get_case_link(self, obj):
        if obj.cases.first():
            return obj.cases.first().url

    def get_site_type(self, obj):
        if obj.cases.first():
            return obj.cases.first().court.site_type

    def get_queryset(self, request):
        qs = self.model.objects.all()

        if request.user.is_superuser:
            return qs
        regions = request.user.regions
        qs = qs.filter(region__in=regions)
        return qs


class UKCaseAdmin(CaseAdmin):
    def get_queryset(self, request):
        qs = self.model.objects.filter(type=2)

        if request.user.is_superuser:
            return qs
        regions = request.user.regions
        qs = qs.filter(court__region__in=regions)
        return qs


class KoapCaseAdmin(CaseAdmin):
    def get_queryset(self, request):
        qs = self.model.objects.filter(type=1)
        if request.user.is_superuser:
            return qs
        regions = request.user.regions
        qs = qs.filter(court__region__in=regions)
        return qs


admin.site.register(UKCase, UKCaseAdmin)
admin.site.register(KoapCase, KoapCaseAdmin)
admin.site.register(Defendant, DefendantAdmin)
