from collections import Counter
from django import forms
from django.contrib import messages
from django.forms import formset_factory
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.core.mail import EmailMessage
from django.utils.translation import gettext as _

from django.views.generic.edit import FormView
from django.views.generic import View

from .models import Customer, Stock, CargoStock
from .models import Cargo, Shipment, ShipmentStock
from .forms import CargoNewForm, CargoFillForm, StockForm, OrderCustomerForm, OrderItemForm, OrderCustomerSelectForm


def index(request):
    return render(request, 'warehouse/index.html')


# class OrderView(FormView):
#     template_name = "warehouse/order.html"
#     form_class = OrderForm
#     # success_url = "order_successful"
#
#     def form_valid(self, form):
#         # return super(OrderView, self).form_valid(form)
#         data = form.cleaned_data
#         customer = Customer.objects.get(id=data['name'])
#         product = Stock.objects.get(article=data['items'])
#         context = {
#             'customer_name': customer.full_name,
#             'customer_id': customer.id,
#             'product_name': product.name,
#             'product_count': data['item_count'],
#         }
#         sh = Shipment.objects.create(customer=customer)
#         ShipmentStock.objects.create(shipment=sh,
#                                      stock=product,
#                                      number=int(data['item_count']))
#         return render(self.request, 'warehouse/order_successful.html', context)
#
#     def get_initial(self):
#         initial = super(OrderView, self).get_initial()
#         customers_list = (Customer.objects
#                           .all()
#                           .order_by('full_name')
#                           .values_list('id', 'full_name'))
#         items_list = Stock.objects.all().values_list('article', 'name')
#         initial.update({'name': customers_list,
#                         'items': items_list})
#         return initial
class OrderView(View):
    OrderItemFormSet = formset_factory(OrderItemForm)

    def post(self, request):
        customer_form = OrderCustomerForm(request.POST)
        item_formset = self.OrderItemFormSet(request.POST)
        customer_selectform = OrderCustomerSelectForm(request.POST)
        context = {
            'customer_form': customer_form,
            'item_formset': item_formset,
            'customer_selectform': customer_selectform,
        }

        if request.POST.get('reg'):
            if customer_selectform.is_valid():
                customer = Customer.objects.get(pk=customer_selectform.cleaned_data.get('customers').pk)
        else:
            if customer_form.is_valid():
                customer = customer_form.save()

        sh = Shipment.objects.create(customer=customer)

        if item_formset.is_valid():
            for form in item_formset:
                product = Stock.objects.get(pk=form.cleaned_data.get('item').pk)
                ShipmentStock.objects.create(shipment=sh,
                                                     stock=product,
                                                     number=int(form.cleaned_data.get('count')))

        return render(request, 'warehouse/order.html', context)

    def get(self, request):
        customer_form = OrderCustomerForm
        item_formset = self.OrderItemFormSet
        customer_selectform = OrderCustomerSelectForm
        context = {
            'customer_form': customer_form,
            'item_formset': item_formset,
            'customer_selectform': customer_selectform,
        }
        return render(request, 'warehouse/order.html', context)


class OrderSuccessfulView(View):
    def get(self, request):
        context = request.GET
        print(context)
        return render(request, 'warehouse/order_successful.html')


def cargo_new(request):
    stock_formset = forms.formset_factory(form=StockForm,
                                          max_num=50,
                                          min_num=1,
                                          extra=0)
    if request.method == 'POST':
        form = CargoNewForm(request.POST)
        formset = stock_formset(request.POST)
        context = {'form': form, 'formset': formset}
        if form.is_valid() and formset.is_valid() and formset.cleaned_data:
            cargo = form.save()
            stocks = {}
            for stock in formset.cleaned_data:
                name = stock['name']
                stocks[name] = stocks.get(name, 0) + stock['number']
            for name, number in stocks.items():
                stock = Stock.objects.get(name=name)
                CargoStock.objects.create(cargo=cargo,
                                          stock=stock,
                                          number=number)
            messages.info(request, _('Заявка отправлена'))
            return redirect(to='warehouse:index')
        else:
            return render(request, 'warehouse/cargo_new.html', context)
    else:
        form = CargoNewForm()
        formset = stock_formset()
        context = {'form': form, 'formset': formset}
        return render(request, 'warehouse/cargo_new.html', context)
    # if request.method == "POST":
    #     form = CargoNewForm(request.POST)
    #     if form.is_valid():
    #         cargo = form.save()
    #         return redirect('warehouse:cargo_detail', pk=cargo.pk)
    # else:
    #     form = CargoNewForm()
    # return render(request, 'warehouse/cargo_new.html', {'form': form})


def cargo_fill(request, pk):
    cargo = get_object_or_404(Cargo, pk=pk)
    if request.method == 'POST':
        form = CargoFillForm(request.POST)
        if form.is_valid():
            form.instance.pk = cargo.pk
            form.instance.date = cargo.date
            form.instance.status = cargo.status
            form.instance.supplier = cargo.supplier
            form.save()
            messages.info(request, _('Заявка отправлена'))
            return redirect('warehouse:index')
        render(request, 'warehouse/cargo_fill.html', {'form': form})
    else:
        form = CargoFillForm()
        form.fields['cargo_supplier'].initial = cargo.supplier
        return render(request, 'warehouse/cargo_fill.html', {'form': form,
                                                             'pk': cargo.pk})


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
