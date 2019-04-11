from django.contrib import admin

from .models import Case, CaseEvent, CaseGroup, Defendant

class CaseAdmin(admin.ModelAdmin):
    list_filter = ('court',)
    list_display = ('__str__', 'court', 'judge', 'entry_date', 'result_date', )

admin.site.register(Case, CaseAdmin)
