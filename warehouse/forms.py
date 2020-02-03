from django import forms


class OrderForm(forms.Form):
    name = forms.CharField()

    def send_email(self):
        pass