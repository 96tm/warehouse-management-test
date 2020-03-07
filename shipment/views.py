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

from category.models import Category
from warehouse.models import Stock
from .models import Shipment
from .forms import OrderItemForm
from .forms import OrderCustomerSelectForm
from customer.forms import CustomerForm
from common.models import ShipmentStock

from django.http import Http404, JsonResponse

from socket import error as socket_base_error


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

        if ((customer_selectform.is_valid() or customer_form.is_valid())
           and item_formset.is_valid()):

            if request.POST.get('reg'):
                customer = customer_selectform.cleaned_data.get('customer')
            else:
                customer = customer_form.save()

            sh = Shipment.objects.create(customer=customer)

            stocks = dict()
            for form in item_formset:
                name = form.cleaned_data['item']
                stocks[name] = (stocks.get(name, 0)
                                + form.cleaned_data.get('count'))
            for stock, count in stocks.items():
                ShipmentStock.objects.create(shipment=sh, stock=stock,
                                             number=count)

            messages.info(request, _('Заявка отправлена'))
            return redirect('shipment:order_successful')

        else:
            return redirect('shipment:order')

    def get(self, request):
        if self.request.is_ajax():
            cat = request.GET['category']
            if cat:
                category = (Category
                            .objects
                            .get(pk=cat).get_descendants(include_self=True))
                stock = Stock.objects.filter(category__in=category)
                stock_dict = {k: v for k, v in stock.values_list('pk', 'name')}
            return JsonResponse(stock_dict)
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

    def get(self, request, qr):
        if qr and Shipment.objects.filter(qr=qr).exists():
            shipment = Shipment.objects.get(qr=qr)
            if shipment.status == Shipment.SENT:
                try:
                    self.send_email_to_admin(request, shipment)
                    messages.info(request, _('Покупка подтверждена, спасибо!'))
                except socket_base_error:
                    messages.error(request,
                                   _('Не удалось подключиться к сети'))
                return render(request, template_name=self.template_name)
        raise Http404(_('Покупка не найдена'))

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
