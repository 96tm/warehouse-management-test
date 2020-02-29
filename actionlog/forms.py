from django import forms

from .models import ModelChangeLogsModel


class ModelChangeLogsModelForm(forms.ModelForm):

    class Meta:
        model = ModelChangeLogsModel
        fields = '__all__'
