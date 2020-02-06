from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import OrderForm
from django.views.generic.edit import FormView
from django.views.generic import View

def index(request):
    return render(request, 'warehouse/index.html')


# страница покупателя
class OrderView(FormView):
    template_name = "warehouse/order.html"
    form_class = OrderForm
    success_url = "order_successful"

    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('order_successful')


class OrderSuccessfulView(View):
    def get(self, request):
        context = request
        return render(request, 'warehouse/order_successful.html')


def supplier(request):
    return render(request, 'warehouse/supplier.html')