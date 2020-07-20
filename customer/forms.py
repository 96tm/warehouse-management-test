
from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):
    """
    Форма покупателя для интерфейса кладовщика.
    """
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {'contact_info': forms.Textarea(attrs={'rows': '2',
                                                         'cols': '34'}),
                   'full_name': forms.TextInput(attrs={'size': '35'}),
                   'phone_number': forms.TextInput(attrs={'size': '35'}),
                   'email': forms.TextInput(attrs={'size': '35'}), }
