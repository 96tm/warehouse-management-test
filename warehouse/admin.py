from django.contrib import admin
from django.utils.translation import gettext as _

from .models import Supplier, Customer, Stock, Category
from .models import Shipment

# функция gettext с псевдонимом _ применяется к строками на английском для последующего перевода


class CustomerAdmin(admin.ModelAdmin):

    class ShipmentInline(admin.StackedInline):
        model = Shipment
        readonly_fields = ('date',)
        fields = ['date', 'status']
        list_display = ['date', 'status']
        can_delete = False
        min_num = 0
        max_num = 0
        verbose_name = _("Shipment")
        verbose_name_plural = _("Shipments")

    inlines = [ShipmentInline, ]
    fieldsets = (
        (_('CUSTOMER DATA'),
         {'fields': ('full_name', 'phone_number',
                     'email', 'contact_info')}),
    )


admin.site.register(Supplier)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Stock)
admin.site.register(Category)
