from django.contrib import admin
from .models import Supplier
from cargo.models import Cargo
from cargo.forms import CargoForm
from .forms import SupplierForm
from django.utils.translation import gettext as _


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """
    Отображение списка и формы поставщиков
    """
    class CargoInline(admin.StackedInline):
        model = Cargo
        form = CargoForm
        min_num = 0
        max_num = 0
        can_delete = False
        show_change_link = True

    form = SupplierForm
    inlines = [CargoInline, ]
    list_display = ('organization', 'email', 'phone_number', 'address',)
    search_fields = ('organization', 'email', 'phone_number', 'address',)
    fieldsets = ((_('ЮРИДИЧЕСКОЕ ЛИЦО'), {'fields':
                                          ('organization',
                                           'address',
                                           'legal_details',)}),
                 (_('КОНТАКТНЫЕ ДАННЫЕ'), {'fields':
                                           ('contact_info',
                                            'phone_number',
                                            'email',)}),
                 (_('КАТЕГОРИИ ТОВАРОВ'), {'fields':
                                           ('supplier_categories',)}))

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.categories.set(form.cleaned_data['supplier_categories'])
