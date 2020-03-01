from django import forms
from django.contrib import messages
from django.views.generic import View
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404

from warehouse.models import Stock
from warehouse.forms import StockForm
from common.models import CargoStock
from .models import Cargo, CargoDetails
from .forms import CargoNewForm, CargoFillForm


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
    template = 'cargo/cargo_formsets.html'

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
            return redirect(to='mainpage:index')
        else:
            if not formset.cleaned_data:
                context['formset'] = self.stock_formset()
            return render(request, self.template, context)

    def get(self, request):
        form = CargoNewForm()
        formset = self.stock_formset()
        context = {'form': form, 'formset': formset}
        return render(request, self.template, context)


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
            return redirect('cargo:cargo_detail', pk=cargo.pk)
    else:
        form = CargoNewForm()
    return render(request, 'cargo/cargo_new.html', {'form': form})


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
    return render(request, 'cargo/cargo_fill.html', context)


def cargo_list(request):
    """
    View для отображения списка поставок
    """
    return render(request, 'cargo/cargo_list.html',
                  {'cargo_all': Cargo.objects.all()})
