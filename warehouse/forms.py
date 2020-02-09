from django import forms


class OrderForm(forms.Form):
    name = forms.ChoiceField(label='Ваше имя: ', choices=())
    items = forms.ChoiceField(label='Выберите товар: ', choices=())

    def __init__(self, *args, **kwargs):
        customers = kwargs.get('initial')['name']
        customers_list = [(k, v) for k,v in customers]
        items = kwargs.get('initial')['items']
        items_list = [('text', t) for t in items]
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['name'].choices = customers_list
        self.fields['items'].choices = items_list
