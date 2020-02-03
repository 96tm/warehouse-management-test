from django.shortcuts import render
from django.http import HttpResponse
from .forms import OrderForm
from django.views.generic.edit import FormView
from django.views.generic import View

def index(request):
    return render(request, 'warehouse/index.html')


# страница покупателя
class OrderView(FormView):
    template_name = "warehouse//order.html"
    form_class = OrderForm
    success_url = "order_successful"

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)


class OrderSuccessfulView(View):
    def get(self, request):
        context = {
            "name": "123",
        }
        return render(request, 'warehouse/order_successful.html', context)


def supplier(request):
    return render(request, 'warehouse/supplier.html')