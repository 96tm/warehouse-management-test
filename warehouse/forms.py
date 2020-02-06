from django import forms


class OrderForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=100)

    def send_email(self):
        pass