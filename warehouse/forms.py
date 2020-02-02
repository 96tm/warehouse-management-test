from django.forms import ModelForm
from .models import Cargo


class CargoForm(ModelForm):
    class Meta:
        model = Cargo
        fields = ('name', 'supplier', 'number',)
