import requests

from django.contrib import messages
from django.forms import formset_factory
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.core.mail import EmailMessage
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .models import Shipment
from .forms import ShipmentConfirmationForm, OrderItemForm
from .forms import OrderCustomerSelectForm
from customer.forms import CustomerForm
from common.models import ShipmentStock


def shipment_success(request):
    """
    View для обработки перенаправления после оформления поставки
    """
    return render(request, 'shipment/shipment_success.html')


@method_decorator(never_cache, name='dispatch')
class OrderView(View):
    """
    Class-based view для обработки страницы покупки
    """
    OrderItemFormSet = formset_factory(OrderItemForm, min_num=1, extra=0)

    def post(self, request):
        customer_form = CustomerForm(request.POST)
        item_formset = self.OrderItemFormSet(request.POST)
        customer_selectform = OrderCustomerSelectForm(request.POST)

        # FIXME: Добавить обработку неправильно введённых форм
        customer = None
        if request.POST.get('reg'):
            if customer_selectform.is_valid():
                customer = customer_selectform.cleaned_data.get('customer')
        else:
            if customer_form.is_valid():
                customer = customer_form.save()
        ###
        if not customer:
            return self.get(request)
        ###
        sh = Shipment.objects.create(customer=customer)

        if item_formset.is_valid():
            stocks = dict()
            for form in item_formset:
                name = form.cleaned_data['item']
                stocks[name] = (stocks.get(name, 0)
                                + form.cleaned_data.get('count'))
            for stock, count in stocks.items():
                ShipmentStock.objects.create(shipment=sh,
                                             stock=stock, number=count)

        messages.info(request, _('Заявка отправлена'))
        return redirect('shipment:order_successful')

    def get(self, request):
        customer_form = CustomerForm()
        item_formset = self.OrderItemFormSet()
        customer_selectform = OrderCustomerSelectForm()
        context = {
            'customer_form': customer_form,
            'item_formset': item_formset,
            'customer_selectform': customer_selectform,
        }
        return render(request, 'shipment/order.html', context)


class OrderSuccessfulView(View):
    """
    Class-based view для обработки перенаправления после покупки
    """

    def get(self, request):
        return render(request, 'shipment/order_successful.html')


class ShipmentConfirmation(TemplateView):
    """
    View для подтверждения получения покупки
    """
    template_name = 'shipment/shipment_confirmation.html'

    def get(self, request):
        return render(request, template_name=self.template_name)

    def post(self, request):
        form = ShipmentConfirmationForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['shipment_key'].strip()
            if key and Shipment.objects.filter(qr=key).exists():
                shipment = Shipment.objects.get(qr=key)
                if shipment.status == Shipment.SENT:
                    messages.info(request, _('Покупка подтверждена, спасибо!'))
                    self.send_email_to_admin(request, shipment)
                    return redirect(to='shipment:shipment_success')
        messages.error(request, _('Покупки с таким ключом не найдено'))
        return render(request, template_name=self.template_name)

    def send_email_to_admin(self, request, shipment):
        body = _('Погрузка доставлена,'
                 + ' вы можете изменить ее статус по ссылке: ')
        body += (request.get_host()
                 + reverse('admin:shipment_shipment_change',
                           args=(shipment.id,)))
        message = EmailMessage(subject=_('Погрузка доставлена'),
                               body=body,
                               to=[settings.ADMINS[0][1], ])
        message.send()
