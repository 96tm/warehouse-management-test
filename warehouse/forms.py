from django import forms
from .models import Cargo, CargoDetails


class CargoNewForm(forms.ModelForm):

    class Meta:
        model = Cargo
        fields = ('supplier',)


class CargoFillForm(forms.ModelForm):

    class Meta:
        model = CargoDetails
        fields = ('order_number', 'name', 'quantity')

