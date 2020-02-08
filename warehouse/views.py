from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelform_factory
from django.http import HttpResponse
from .models import Cargo, CargoDetails, Supplier
from .forms import CargoNewForm, CargoFillForm
# Create your views here.


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
            cargo = form.save()
            cargo.save()
            return redirect('warehouse:cargo_detail', pk=cargo.pk)
    else:
        form = CargoNewForm()
    return render(request, 'warehouse/cargo_new.html', {'form': form})


def cargo_fill(request, pk):
    context = {}
    context['cargo'] = get_object_or_404(Cargo, pk=pk)
    context['items'] = CargoDetails.objects.filter(order_number=pk)
    if request.method == 'POST':
        form = CargoFillForm(request.POST)
        if form.is_valid():
            form.save()
    context['form'] = CargoFillForm(initial={'order_number': pk})
    return render(request, 'warehouse/cargo_fill.html', context)


def cargo_list(request):
    cargo_all = Cargo.objects.all()
    return render(request, 'warehouse/cargo_list.html', {'cargo_all': cargo_all})
