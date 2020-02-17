from django import forms

from django.utils.translation import gettext as _
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Supplier, Customer, Category
from .models import Shipment, Cargo, CargoStock, Stock
from .models import format_date, get_parent_categories
from .models import get_shipment_total, get_cargo_total


class CategoryForm(forms.ModelForm):
    """
    Форма для отображения категории в интерфейсе кладовщика
    """
    class Meta:
        model = Category
        fields = ('name', )
    parent_name = forms.ChoiceField(label=_('Базовая категория'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            choices = get_parent_categories(self.instance.pk)
            initial = ((self.instance.parent_id, self.instance.name)
                       if self.instance.parent_id
                       else choices[0])
            self.fields['parent_name'].choices = choices
            self.fields['parent_name'].initial = initial


class OrderFormsetsForm(forms.ModelForm):
    """
    Форма для заполнения информации о покупке (добавляется несколько товаров)
    """
    class Meta:
        model = Shipment
        fields = ('customer', )


class OrderCustomerForm(forms.ModelForm):
    full_name = forms.CharField(required=False, label='ФИО')
    email = forms.EmailField(required=False, label='E-mail')
    contact_info = forms.CharField(required=False, label='Контактная информация', widget=forms.Textarea())
    phone_number = forms.CharField(required=False, label='Телефон')

    class Meta:
        model = Customer
        fields = '__all__'


class OrderCustomerSelectForm(forms.Form):
    customers = forms.ModelChoiceField(queryset=Customer.objects.all(),
                                       required=False)


class OrderItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Stock.objects.all(), required=True)
    count = forms.DecimalField(required=True, initial=1, min_value=1)


class CargoNewForm(forms.ModelForm):
    """
    Форма для выбора поставщика
    при оформлении поставки
    """
    class Meta:
        model = Cargo
        fields = ('supplier', )


class CargoFillForm(forms.ModelForm):
    """
    Форма заполнения информации о товаре
    при оформлении поставки
    """
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

    def save(self, commit=True):
        stock = Stock.objects.get(name=self.cleaned_data['stock_name'])
        CargoStock.objects.create(cargo=self.instance,
                                  stock=stock,
                                  number=self.cleaned_data['number'])
        super().save(commit)


class CargoForm(forms.ModelForm):
    """
    Форма поставки для интерфейса кладовщика
    """
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
            number = current_cargo.cargostock_set.count()
            total = get_cargo_total(current_cargo)
            supplier = current_cargo.supplier.organization
            date = current_cargo.date
            self.fields['cargo_id'].initial = current_cargo.id
            self.fields['cargo_status'].initial = current_cargo.status
            self.fields['cargo_date'].initial = format_date(date)
            self.fields['cargo_supplier'].initial = supplier
            self.fields['number'].initial = number
            self.fields['total'].initial = total


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

    field_order = ['number_of_items', 'total', 'customer_name',
                   'shipment_id', 'shipment_date',
                   'shipment_status', 'shipment_qr']

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


class StockForm(forms.Form):
    """
    Форма заказа для страниц оформления покупки и поставки
    """
    name = forms.ChoiceField(required=True, label=_("Товар"))
    number = forms.IntegerField(min_value=1,
                                required=True,
                                label=_("Количество"))
    number.widget = forms.NumberInput(attrs={'required': 'required',
                                             'value': '1',
                                             'min': '1',
                                             'max': '99'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(Stock.objects.values_list('name', 'name'))
        self.fields['name'].choices = choices
        self.fields['number'].initial = 1


class StockFormM2M(forms.ModelForm):
    """
    Форма товара для отображения
    в поставках и покупках в интерфейсе кладовщика
    """
    class Meta:
        fields = []
    stock_name = forms.CharField(label=_('Наименование'))
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
            self.fields['stock_name'].initial = cargo_stock.stock.name


class CustomerForm(forms.ModelForm):
    """
    Форма покупателя для интерфейса кладовщика
    """
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {'contact_info': forms.Textarea(attrs={'rows': '2',
                                                         'cols': '34'}),
                   'full_name': forms.TextInput(attrs={'size': '35'}),
                   'phone_number': forms.TextInput(attrs={'size': '35'}),
                   'email': forms.TextInput(attrs={'size': '35'}), }


class SupplierForm(forms.ModelForm):
    """
    Форма поставщика для интерфейса кладовщика
    """
    class Meta:
        model = Supplier
        fields = ['organization', 'phone_number', 'email',
                  'address', 'legal_details', 'contact_info', 'categories', ]
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
        label=_(''),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('категория'),
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
