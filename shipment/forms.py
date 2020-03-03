from django import forms

from django.utils.translation import gettext as _
from mptt.forms import TreeNodeChoiceField

from category.models import Category
from .models import Shipment
from common.models import format_date
from .models import get_shipment_total

from warehouse.models import Stock
from customer.models import Customer


class ShipmentForm(forms.ModelForm):
    """
    Форма покупки для интерфейса кладовщика
    """
    class Meta:
        model = Shipment
        fields = []

    # дополнительные поля для формы
    number_of_items = forms.CharField(max_length=10,
                                      label=_('Количество позиций'))
    total = forms.CharField(max_length=10, label=_('Сумма заказа'))
    customer_name = forms.CharField(max_length=80, label=_('Покупатель'))
    shipment_id = forms.CharField(max_length=10, label=_('Номер заказа'))
    shipment_date = forms.CharField(max_length=19, label=_('Дата заказа'))
    shipment_status = forms.CharField(max_length=9, label=_('Статус заказа'))
    shipment_qr = forms.CharField(max_length=50, label=_('Код подтверждения'))

    field_order = ('number_of_items', 'total', 'customer_name',
                   'shipment_id', 'shipment_date',
                   'shipment_status', 'shipment_qr', )

    # добавляем инициализацию дополнительных полей при создании формы
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            current_shipment = self.instance
            for key, value in self.fields.items():
                value.widget = forms.TextInput({'size': '35',
                                                'readonly': 'readonly'})
                value.required = False

            # сумма погрузки
            money = get_shipment_total(current_shipment)
            # общее количество всех товаров погрузки
            number = current_shipment.shipmentstock_set.count()
            date = format_date(current_shipment.date)
            values = (number, money, current_shipment.customer.full_name,
                      current_shipment.id, date, current_shipment.status,
                      current_shipment.qr)
            for index, field_name in enumerate(self.field_order):
                self.fields[field_name].initial = values[index]


class ShipmentConfirmationForm(forms.Form):
    """
    Форма с полем ввода ключа для подтверждения получения покупки
    """
    shipment_key = forms.CharField(required=True)


class OrderCustomerSelectForm(forms.Form):
    """
    Форма для выбора покупателя на странице покупки
    """
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(),
                                      label=_('Покупатель'))
    customer.widget = forms.Select(attrs={'disabled': 'disabled'})


class OrderItemForm(forms.Form):
    """
    Форма для выбора товара на странице покупки
    """
    category = TreeNodeChoiceField(queryset=Category.objects.all(),
                                   level_indicator=u'+--', required=False)
    category.widget = forms.Select(attrs={'class': "category"})
    item = forms.ModelChoiceField(queryset=Stock.objects.all())
    item.widget = forms.Select(attrs={'required': True})
    count = forms.DecimalField(required=True, initial=1, min_value=1)

