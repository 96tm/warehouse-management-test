from django.shortcuts import render,  get_object_or_404
from django.forms import modelform_factory
from .models import Cargo, CargoDetails
from django.http import HttpResponse
# Create your views here.
from .models import Supplier
from .forms import CargoNewForm, CargoFillForm


def index(request):
    return render(request, 'warehouse/index.html')


def customer(request):
    return render(request, 'warehouse/customer.html')


def supplier(request):
    # suppliers = Supplier.objects.all().order_by('organization')
    return render(request, 'warehouse/supplier.html')


def cargo_new(request):
    if request.method == "POST":
        form = CargoNewForm(request.POST)
        if form.is_valid():
            form.save()
    form = CargoNewForm()
    return render(request, 'warehouse/cargo_new.html', {'form': form})


# def cargo_fill(request):
#     if request.method == 'POST':
#         form = CargoFillForm(request.POST)
#         if form.is_valid():
#             form.save()
#     form = CargoFillForm()
#     return render(request, 'warehouse/cargo_fill.html', {'form': form})

def cargo_fill(request, pk):
    cargo = get_object_or_404(Cargo, pk=pk)
    return render(request, 'warehouse/cargo_fill.html', {'cargo': cargo})


def cargo_list(request):
    cargo_all = Cargo.objects.all()
    return render(request, "warehouse/cargo_list.html", {'cargo_all': cargo_all})

