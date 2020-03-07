from django import forms
from django.contrib import messages
from django.views.generic import View
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect

from warehouse.models import Stock
from warehouse.forms import StockForm
from common.models import CargoStock
from .forms import CargoNewForm


# не кэшируем страницу для нормальной работы кода jQuery
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
