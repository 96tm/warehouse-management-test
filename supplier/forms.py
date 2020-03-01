from django import forms

from django.utils.translation import gettext as _
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Supplier
from category.models import Category


class SupplierForm(forms.ModelForm):
    """
    Форма поставщика для интерфейса кладовщика
    """
    class Meta:
        model = Supplier
        fields = ('organization', 'phone_number', 'email',
                  'address', 'legal_details', 'contact_info', 'categories', )
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
