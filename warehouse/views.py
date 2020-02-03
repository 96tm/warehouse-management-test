from django.shortcuts import render,  get_object_or_404
from django.forms import modelform_factory
from .models import Cargo, CargoDetails
from django.http import HttpResponse
# Create your views here.
from .models import Supplier
from .forms import NeworderForm, OrderdetailsForm


def index(request):
    return render(request, 'warehouse/index.html')


def customer(request):
    return render(request, 'warehouse/customer.html')


def supplier(request):
    # suppliers = Supplier.objects.all().order_by('organization')
    return render(request, 'warehouse/supplier.html')


def neworder(request):
    if request.method == "POST":
        form = NeworderForm(request.POST)
        if form.is_valid():
            form.save()
    form = NeworderForm()
    return render(request, 'warehouse/order_new.html', {'form': form})


def orderdetails(request):
    if request.method == 'POST':
        form = OrderdetailsForm(request.POST)
        if form.is_valid():
            form.save()
    form = OrderdetailsForm()
    return render(request, 'warehouse/order_details.html', {'form': form})


def orders_list(request):
    orders = Cargo.objects.all()
    return render(request, "warehouse/order_list.html", {'orders': orders})
