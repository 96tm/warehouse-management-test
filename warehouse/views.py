import requests

from django import forms
from django.contrib import messages
from django.forms import formset_factory
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.core.mail import EmailMessage
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .models import Stock, CargoStock
from .models import CargoDetails, ShipmentStock
from .models import Cargo, Shipment
from .forms import CustomerForm, OrderItemForm, OrderCustomerSelectForm
from .forms import CargoNewForm, CargoFillForm, StockForm, ShipmentConfirmationForm


def index(request):
    return render(request, 'warehouse/index.html')


# не кэшируем страницу для нормальной работы jQuery кода
# по добавлению formsets
@method_decorator(never_cache, name='dispatch')
class CargoFormsetsView(View):
    """
    Class-based view для обработки страницы
    поставки с добавлением нескольких товаров
    в одной форме
    """
    stock_formset = forms.formset_factory(form=StockForm,
                                          max_num=50,
                                          min_num=1,
                                          extra=0)
    template = 'warehouse/cargo_formsets.html'

    def post(self, request):
        form = CargoNewForm(request.POST)
        formset = self.stock_formset(request.POST)
        context = {'form': form, 'formset': formset}
        if form.is_valid() and formset.is_valid() and formset.cleaned_data:
            instance = form.save()
            stocks = {}
            for stock in formset.cleaned_data:
                name = stock['name']
                stocks[name] = stocks.get(name, 0) + stock['number']
            for name, number in stocks.items():
                stock = Stock.objects.get(name=name)
                CargoStock.objects.create(cargo=instance,
                                          stock=stock, number=number)
            messages.info(request, _('Заявка отправлена'))
            return redirect(to='warehouse:index')
        else:
            if not formset.cleaned_data:
                context['formset'] = self.stock_formset()
            return render(request, self.template, context)

    def get(self, request):
        form = CargoNewForm()
        formset = self.stock_formset()
        context = {'form': form, 'formset': formset}
        return render(request, self.template, context)


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

        if request.POST.get('reg'):
            if customer_selectform.is_valid():
                customer = customer_selectform.cleaned_data.get('customer')
        else:
            if customer_form.is_valid():
                customer = customer_form.save()

        sh = Shipment.objects.create(customer=customer)

        if item_formset.is_valid():
            stocks = dict()
            for form in item_formset:
                name = form.cleaned_data['item']
                stocks[name] = stocks.get(name, 0) + form.cleaned_data.get('count')
            for stock, count in stocks.items():
                ShipmentStock.objects.create(shipment=sh, stock=stock, number=count)

        messages.info(request, _('Заявка отправлена'))
        return redirect('warehouse:order_successful')

    def get(self, request):
        customer_form = CustomerForm()
        item_formset = self.OrderItemFormSet()
        customer_selectform = OrderCustomerSelectForm()
        context = {
            'customer_form': customer_form,
            'item_formset': item_formset,
            'customer_selectform': customer_selectform,
        }
        return render(request, 'warehouse/order.html', context)


class OrderSuccessfulView(View):
    """
    Class-based view для обработки перенаправления после покупки
    """

    def get(self, request):
        return render(request, 'warehouse/order_successful.html')


def cargo_new(request):
    """
    View для выбора поставщика
    при добавлении товаров с использованием
    таблицы CargoDetails
    """
    if request.method == "POST":
        form = CargoNewForm(request.POST)
        if form.is_valid():
            cargo = form.save()
            return redirect('warehouse:cargo_detail', pk=cargo.pk)
    else:
        form = CargoNewForm()
    return render(request, 'warehouse/cargo_new.html', {'form': form})


def cargo_fill(request, pk):
    """
    View для добавления информации о товаре
    при использовании таблицы CargoDetails
    """
    cargo = get_object_or_404(Cargo, pk=pk)
    items = CargoDetails.objects.filter(order_number=pk)
    if request.method == 'POST':
        form = CargoFillForm(request.POST)
        if form.is_valid():
            form.save()
    form = CargoFillForm(initial={'order_number': pk})
    context = {'cargo': cargo,
               'items': items,
               'form': form}
    return render(request, 'warehouse/cargo_fill.html', context)


def cargo_list(request):
    """
    View для отображения списка поставок
    """
    return render(request, 'warehouse/cargo_list.html',
                  {'cargo_all': Cargo.objects.all()})


def shipment_success(request):
    """
    View для обработки перенаправления после оформления поставки
    """
    return render(request, 'warehouse/shipment_success.html')


class ShipmentConfirmation(TemplateView):
    """
    View для подтверждения получения покупки
    """
    template_name = 'warehouse/shipment_confirmation.html'

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
                    self.send_email_to_admin_mailgun(request, shipment)
                    return redirect(to='warehouse:shipment_success')
        messages.error(request, _('Покупки с таким ключом не найдено'))
        return render(request, template_name=self.template_name)

    def send_email_to_admin(self, request, shipment):
        body = _('Погрузка доставлена,'
                 + ' вы можете изменить ее статус по ссылке: ')
        body += (request.get_host()
                 + reverse('admin:warehouse_shipment_change',
                           args=(shipment.id,)))
        message = EmailMessage(subject=_('Погрузка доставлена'),
                               body=body,
                               to=[settings.ADMINS[0][1], ])
        message.send()

    def send_email_to_admin_mailgun(self, request, shipment):
            body = _('Погрузка доставлена,'
                    + ' вы можете изменить ее статус по ссылке: ')
            body += (request.get_host()
                    + reverse('admin:warehouse_shipment_change',
                            args=(shipment.id,)))                                                                                                                  
            return requests.post("https://api.mailgun.net/v3/sandboxb9935d22024f479d9c4f54ace37bb83b.mailgun.org/messages",
                            auth=("api", "9cc351040b43bf8524fce5e31bedaeaf-7238b007-e0e2b8c2"),
                            data={"from": "admin <mailgun@sandboxb9935d22024f479d9c4f54ace37bb83b.mailgun.org>",
                            "to": [settings.ADMINS[0][1], ], "subject": _('Погрузка доставлена'), "text": body,
                            "html": '<html>'+body+'</html>'})
