from .models import Cargo, CargoDetails, Shipment
from .forms import CargoNewForm, CargoFillForm

from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings
from django.views.generic import TemplateView
from django.core.mail import EmailMessage
from django.utils.translation import gettext as _


def index(request):
    return render(request, 'warehouse/index.html')


def customer(request):
    return render(request, 'warehouse/customer.html')


def supplier(request):
    return render(request, 'warehouse/supplier.html')


def cargo_new(request):
    if request.method == "POST":
        form = CargoNewForm(request.POST)
        if form.is_valid():
            cargo = form.save()
            cargo.save()
            return redirect('warehouse:cargo_detail', pk=cargo.pk)
    else:
        form = CargoNewForm()
    return render(request, 'warehouse/cargo_new.html', {'form': form})


def cargo_fill(request, pk):
    context = {}
    context['cargo'] = get_object_or_404(Cargo, pk=pk)
    context['items'] = CargoDetails.objects.filter(order_number=pk)
    if request.method == 'POST':
        form = CargoFillForm(request.POST)
        if form.is_valid():
            form.save()
    context['form'] = CargoFillForm(initial={'order_number': pk})
    return render(request, 'warehouse/cargo_fill.html', context)


def cargo_list(request):
    cargo_all = Cargo.objects.all()
    return render(request, 'warehouse/cargo_list.html', {'cargo_all': cargo_all})

def shipment_success(request):
    return render(request, 'warehouse/shipment_success.html')


class ShipmentConfirmation(TemplateView):
    template_name = 'warehouse/shipment_confirmation.html'

    def get(self, request):
        return render(request, template_name=self.template_name)

    def post(self, request):
        form = self.ShipmentConfirmationForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['shipment_key'].strip()
            if key and Shipment.objects.filter(qr=key).exists():
                shipment = Shipment.objects.get(qr=key)
                if shipment.status == Shipment.SENT:
                    self.send_email_to_admin(request, shipment)
                    return redirect(to='warehouse:shipment_success')
            error_message = _('Покупки с таким ключом не найдено')
            return render(request, template_name=self.template_name,
                          context={'error_messages': [error_message]})
        else:
            return render(request, template_name=self.template_name)

    def send_email_to_admin(self, request, shipment):
        body = _('Погрузка доставлена,'
                 + ' вы можете изменить ее статус по ссылке: ')
        body += (request.get_host()
                 + reverse('admin:warehouse_shipment_change',
                           args=(shipment.id, )))
        message = EmailMessage(subject=_('Погрузка доставлена'),
                               body=body,
                               to=[settings.ADMINS[0][1], ])
        message.send()

    class ShipmentConfirmationForm(forms.Form):
        shipment_key = forms.CharField(required=True)
