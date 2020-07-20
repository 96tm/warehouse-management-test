from django import forms

from django.utils.translation import gettext as _

from .models import Cargo, get_cargo_total
from common.models import format_date


class CargoNewForm(forms.ModelForm):
    """
    Форма для выбора поставщика
    при оформлении поставки.
    """
    class Meta:
        model = Cargo
        fields = ('supplier', )


class CargoForm(forms.ModelForm):
    """
    Форма поставки для интерфейса кладовщика.
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
