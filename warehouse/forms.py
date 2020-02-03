from django import forms
from .models import Cargo, CargoDetails


class NeworderForm(forms.ModelForm):

    class Meta:
        model = Cargo
        fields = ('supplier',)


class OrderdetailsForm(forms.ModelForm):

    class Meta:
        model = CargoDetails
        fields = ('order_number', 'name', 'quantity')
