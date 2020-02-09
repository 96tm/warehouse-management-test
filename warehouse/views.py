from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

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