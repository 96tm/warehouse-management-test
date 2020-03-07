from django import forms

from .models import LogModel


class LogModelForm(forms.ModelForm):

    class Meta:
        model = LogModel
        fields = '__all__'
