from django import forms
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.mail import EmailMessage
from django.utils.translation import gettext as _
from .models import Shipment
from .forms import OrderForm
from django.views.generic.edit import FormView
from django.views.generic import View
from .models import Customer, Stock

def index(request):
    return render(request, 'warehouse/index.html')


# страница покупателя
# def order_view(request):
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             return HttpResponseRedirect('order_successful')
#
#     else:
#         form = OrderForm()
#
#     return render(request, 'warehouse/order.html', {'form': form})

class OrderView(FormView):
    template_name = "warehouse/order.html"
    form_class = OrderForm
    # success_url = "order_successful"

    def form_valid(self, form):
        # return super(OrderView, self).form_valid(form)
        data = form.cleaned_data
        customer = Customer.objects.get(id=data['name'])
        print(data)
        print(customer)
        context = {
            'customer_name': customer.full_name,
            'customer_id': customer.id
        }
        return render(self.request, 'warehouse/order_successful.html', context)

    def get_initial(self):
        initial = super(OrderView, self).get_initial()
        customers_list = Customer.objects.all().order_by('full_name').values_list('id', 'full_name')
        items_list = Stock.objects.all().values_list()
        initial.update({'name': customers_list,
                        'items': ['1', '2', '3']})
        print('1', initial)
        return initial


class OrderSuccessfulView(View):
    def get(self, request):
        context = request.GET
        print(context)
        return render(request, 'warehouse/order_successful.html')


def supplier(request):
    return render(request, 'warehouse/supplier.html')


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
