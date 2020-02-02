from django.shortcuts import render, HttpResponseRedirect, reverse
from .forms import CargoForm
from django.forms import modelformset_factory
from django.http import HttpResponse
from .models import Cargo
# Create your views here.


def index(request):
    return render(request, 'warehouse/index.html')


def customer(request):
    return render(request, 'warehouse/customer.html')


def supplier(request):
    return render(request, 'warehouse/supplier.html')


def supply(request):
    # if request.method == 'POST':
    #     form = CargoForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return HttpResponseRedirect('supply')
    # return render(request, 'warehouse/supply.html', {
    #     'form': CargoForm(),
    # })

    supply_formset = modelformset_factory(Cargo, fields=('name', 'supplier', 'number',))
    if request.method == 'POST':
        form = supply_formset(request.POST)
        if form.is_valid():
            form.save()
        # instances = form.save()
    form = supply_formset(queryset=Cargo.objects.none())

    return render(request, 'warehouse/supply.html', {'form': form})
