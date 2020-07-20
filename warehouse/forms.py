from django import forms

from django.utils.translation import gettext as _

from .models import Stock


class StockPriceFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price_from'] = forms.FloatField(label='', required=False)
        attrs = {'placeholder': _('От')}
        self.fields['price_from'].widget = forms.NumberInput(attrs=attrs)
        self.fields['price_to'] = forms.FloatField(label='', required=False)
        attrs = {'placeholder': _('До')}
        self.fields['price_to'].widget = forms.NumberInput(attrs=attrs)


class StockForm(forms.Form):
    """
    Форма заказа для страниц оформления покупки и поставки.
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
