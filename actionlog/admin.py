from django.contrib import admin

from .forms import ModelChangeLogsModelForm
from .models import ModelChangeLogsModel


@admin.register(ModelChangeLogsModel)
class LogAdmin(admin.ModelAdmin):
    form = ModelChangeLogsModelForm
    list_display = ('id', 'table_name', 'data', 'action', 'date', )
    fields = list_display
    list_filter = ('table_name', 'date', 'action', )
    search_fields = ('data', )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
