import pytz

from django import forms

from django.utils.translation import gettext as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Sum
from django.conf import settings

from .models import Supplier, Customer, Category, CargoDetails
from .models import Shipment, ShipmentStock, Cargo, CargoStock, Stock


def format_date(date):
    return (date
            .astimezone(tz=pytz.timezone(settings.TIME_ZONE))
            .strftime('%Y-%m-%d %H:%M:%S'))


class OrderForm(forms.Form):
    name = forms.ChoiceField(label=_('Ваше имя'))
    items = forms.ChoiceField(label=_('Выберите товар'))
    item_count = forms.DecimalField(label=_('Количество товара'),
                                    initial=1, min_value=1)

    def __init__(self, *args, **kwargs):
        customers = kwargs.get('initial')['name']
        customers_list = [(k, v) for k, v in customers]
        items = kwargs.get('initial')['items']
        items_list = [(k, v) for k, v in items]
        super().__init__(*args, **kwargs)
        self.fields['name'].choices = customers_list
        self.fields['items'].choices = items_list


class CargoNewForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ('supplier', )


class CargoFillForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = []

    cargo_supplier = forms.CharField(label=_('Поставщик'))
    cargo_supplier.widget = forms.TextInput(attrs={'readonly': 'readonly'})
    number = forms.IntegerField(label=_('Количество позиций'), initial=1,
                                min_value=1)
    stock_name = forms.ChoiceField(label=_("Наименование товара"), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(s.name, s.name) for s in Stock.objects.all()]
        self.fields['stock_name'].choices = choices

    def save(self):
        stock = Stock.objects.get(name=self.cleaned_data['stock_name'])
        CargoStock.objects.create(cargo=self.instance,
                                  stock=stock,
                                  number=self.cleaned_data['number'])
        super().save()


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = []

    cargo_id = forms.CharField(label=_('Номер поставки'))
    cargo_supplier = forms.CharField(label=_('Поставщик'))
    cargo_status = forms.CharField(label=_('Статус поставки'))
    cargo_date = forms.CharField(label=_('Дата поставки'))
    number = forms.CharField(label=_('Количество позиций'))
    total = forms.CharField(label=_('Сумма поставки'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            current_cargo = self.instance
            for key, value in self.fields.items():
                value.widget = forms.TextInput({'size': '35',
                                                'readonly': 'readonly'})
                value.required = False
            cargo_stocks = (CargoStock
                            .objects
                            .filter(cargo=current_cargo)
                            .select_related('stock'))
            number = sum([cargo_stock.number for cargo_stock in cargo_stocks])
            total = sum([cargo_stock.stock.price * cargo_stock.number
                        for cargo_stock in cargo_stocks])
            supplier = current_cargo.supplier.organization
            date = current_cargo.date
            self.fields['cargo_id'].initial = current_cargo.id
            self.fields['cargo_status'].initial = current_cargo.status
            self.fields['cargo_date'].initial = format_date(date)
            self.fields['cargo_supplier'].initial = supplier
            self.fields['number'].initial = number
            self.fields['total'].initial = total


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = []

    # дополнительные поля для формы
    number_of_items = forms.CharField(max_length=10,
                                      label=_('Количество товаров'))
    total = forms.CharField(max_length=10, label=_('Сумма покупки'))
    customer_name = forms.CharField(max_length=80, label=_('Покупатель'))
    shipment_id = forms.CharField(max_length=10, label=_('Номер заказа'))
    shipment_date = forms.CharField(max_length=19, label=_('Дата заказа'))
    shipment_status = forms.CharField(max_length=9, label=_('Статус заказа'))
    shipment_qr = forms.CharField(max_length=50, label=_('Код подтверждения'))

    field_order = ['number_of_items', 'total', 'customer_name',
                   'shipment_id', 'shipment_date',
                   'shipment_status', 'shipment_qr']

    # добавляем инициализацию дополнительных полей при создании формы
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs.get('instance'):
            current_shipment = kwargs['instance']
            for key, value in self.fields.items():
                value.widget = forms.TextInput({'size': '35',
                                                'readonly': 'readonly'})
                value.required = False
            # выбираем записи из many-to-many таблицы shipmentstock,
            # относящиеся к выбранной погрузке,
            # к каждой записи добавляем цену соответствующего товара из stocks
            shipment_stocks = (ShipmentStock
                               .objects.select_related('stock')
                               .filter(shipment=current_shipment))
            # сумма погрузки
            money = sum([shipment_stock.stock.price * shipment_stock.number
                         for shipment_stock in shipment_stocks])
            # общее количество всех товаров погрузки
            number = (ShipmentStock.objects
                      .filter(shipment=current_shipment)
                      .aggregate(Sum('number')))['number__sum']
            date = format_date(current_shipment.date)
            values = (number, money, current_shipment.customer.full_name,
                      current_shipment.id, date, current_shipment.status,
                      current_shipment.qr)
            for index, field_name in enumerate(self.field_order):
                self.fields[field_name].initial = values[index]


class StockForm(forms.Form):
    name = forms.ChoiceField(required=True, label=_("Товар"))
    number = forms.IntegerField(min_value=1,
                                required=True,
                                label=_("Количество"))
    number.widget = forms.NumberInput(attrs={'required': 'required',
                                             'value': '1'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(Stock.objects.values_list('name', 'name'))
        self.fields['name'].choices = choices
        self.fields['number'].initial = 1


class StockFormM2M(forms.ModelForm):
    class Meta:
        fields = []

    stock_article = forms.CharField(label=_('Артикул'))
    stock_number = forms.CharField(label=_('Количество на складе'))
    cargo_number = forms.CharField(label=_('Количество в заявке'))
    stock_price = forms.CharField(label=_('Цена за штуку'))
    stock_category = forms.CharField(label=_('Категория'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            for key, value in self.fields.items():
                value.widget = forms.TextInput({'size': '35',
                                                'readonly': 'readonly'})
                value.required = False

            cargo_stock = self.instance
            self.fields['stock_number'].initial = cargo_stock.stock.number
            self.fields['cargo_number'].initial = cargo_stock.number
            self.fields['stock_price'].initial = cargo_stock.stock.price
            self.fields['stock_article'].initial = cargo_stock.stock.article
            self.fields['stock_category'].initial = cargo_stock.stock.category


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {'contact_info': forms.Textarea(attrs={'rows': '2',
                                                         'cols': '34'}),
                   'full_name': forms.TextInput(attrs={'size': '35'}),
                   'phone_number': forms.TextInput(attrs={'size': '35'}),
                   'email': forms.TextInput(attrs={'size': '35'}), }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['organization', 'phone_number', 'email',
                  'address',  'legal_details', 'contact_info', 'categories']
        widgets = {'organization': forms.Textarea(attrs={'rows': '2',
                                                         'cols': '80'}),
                   'address': forms.Textarea(attrs={'rows': '2',
                                                    'cols': '80'}),
                   'legal_details': forms.Textarea(attrs={'rows': '2',
                                                          'cols': '80'}),
                   'contact_info': forms.Textarea(attrs={'rows': '2',
                                                         'cols': '80'})}

    supplier_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Категория'),
            is_stacked=False
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            initial = (self
                       .instance
                       .suppliercategory_set
                       .select_related('category'))
            self.fields['supplier_categories'].initial = [i.category
                                                          for i in initial]
