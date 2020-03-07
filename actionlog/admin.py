from django.contrib import admin

from django.shortcuts import reverse

from .forms import LogModelForm
from .models import LogModel

from shipment.models import Shipment
from cargo.models import Cargo
from supplier.models import Supplier
from customer.models import Customer


@admin.register(LogModel)
class LogAdmin(admin.ModelAdmin):
    form = LogModelForm
    list_display = ('id', 'table_name', 'data', 'action', 'date', )
    fields = list_display
    list_filter = ('table_name', 'date', 'action', )
    search_fields = ('data', )

    def check_if_object_exists(self, log_entry):
        exists = False
        object_entry_id = log_entry.object_entry_id
        if log_entry.table_name == Shipment._meta.verbose_name:
            exists = Shipment.objects.filter(pk=object_entry_id).exists()
        elif log_entry.table_name == Cargo._meta.verbose_name:
            exists = Cargo.objects.filter(pk=object_entry_id).exists()
        elif log_entry.table_name == Customer._meta.verbose_name:
            exists = Customer.objects.filter(pk=object_entry_id).exists()
        else:
            exists = Supplier.objects.filter(pk=object_entry_id).exists()
        return exists

    def get_model_name(self, log_entry):
        name = ''
        if log_entry.table_name == Shipment._meta.verbose_name:
            name = Shipment.__name__
        elif log_entry.table_name == Cargo._meta.verbose_name:
            name = Cargo.__name__
        elif log_entry.table_name == Customer._meta.verbose_name:
            name = Customer.__name__
        else:
            name = Supplier.__name__
        return name

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id,
                    form_url='', extra_context=None):
        extra_context = extra_context or {}
        if LogModel.objects.filter(pk=object_id).exists():
            log_entry = LogModel.objects.get(pk=object_id)
            exists = self.check_if_object_exists(log_entry)
            if exists:
                extra_context['object_exists'] = exists
                model_name = self.get_model_name(log_entry).lower()
                app_name = model_name
                url_to_reverse = ('admin:'
                                  + app_name + '_' + model_name + '_change')
                link = reverse(url_to_reverse,
                               args=(log_entry.object_entry_id, ))
                extra_context['object_link'] = link
        return super().change_view(request, object_id,
                                   form_url='', extra_context=extra_context)
