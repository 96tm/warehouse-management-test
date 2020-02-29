from django.contrib import admin
from django.utils.translation import gettext as _

from .forms import CargoForm
from warehouse.forms import StockFormM2M

from .models import Cargo
from common.models import CargoStock


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    """
    Отображение списка и формы поставок
    """

    class StockInline(admin.StackedInline):
        model = CargoStock
        form = StockFormM2M
        max_num = 0
        min_num = 0
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')
        can_delete = False

    form = CargoForm
    # поля для отображения в списке поставок
    list_display = ('supplier', 'date', 'status',)
    # поля для фильтрации
    list_filter = ('date', 'supplier', 'status',)
    # поля для текстового поиска
    search_fields = ['supplier__organization', ]
    fieldsets = ((_('ИНФОРМАЦИЯ О ПОСТАВКЕ'),
                  {'fields': ('cargo_id', 'cargo_supplier',
                              'cargo_status', 'cargo_date',
                              'number', 'total')}),)
    inlines = [StockInline, ]

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id,
                    form_url='', extra_context=None):
        extra = extra_context or {}
        extra['STATUS_VALUE'] = Cargo.objects.get(pk=object_id).status
        extra['STATUS_IN_TRANSIT'] = Cargo.IN_TRANSIT
        extra['STATUS_DONE'] = Cargo.DONE
        return super().change_view(request, object_id,
                                   form_url,
                                   extra_context=extra)

    def save_model(self, request, obj, form, change):
        if '_confirm' in request.POST and obj.status == Cargo.IN_TRANSIT:
            cargo_stocks = CargoStock.objects.filter(cargo=obj)
            for cs in cargo_stocks:
                cs.stock.number += cs.number
                cs.stock.save()
            obj.status = Cargo.DONE
        super().save_model(request, obj, form, change)

