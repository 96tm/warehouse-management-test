from django.contrib import admin
from django.utils.translation import gettext as _

from .models import Customer

from shipment.models import Shipment
from shipment.forms import ShipmentForm
from .forms import CustomerForm


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Отображение списка и формы покупателей
    """

    # объект для отображения заказов выбранного покупателя
    class ShipmentInline(admin.StackedInline):
        form = ShipmentForm
        model = Shipment
        can_delete = False
        min_num = 0
        max_num = 0
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        show_change_link = True

    form = CustomerForm
    list_display = ('full_name', 'email', 'phone_number',)
    search_fields = ('full_name', 'email', 'phone_number',)
    inlines = [ShipmentInline, ]

    fieldsets = (
        (_('ДАННЫЕ ПОКУПАТЕЛЯ'),
         {'fields': ('full_name', 'phone_number',
                     'email', 'contact_info')}),
    )

