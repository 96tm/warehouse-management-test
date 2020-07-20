from django.contrib.admin import ListFilter, SimpleListFilter
from django.utils.translation import gettext as _
from django.utils.html import mark_safe

from .forms import StockPriceFilterForm
from category.models import Category

from mptt.admin import TreeRelatedFieldListFilter

from common.models import subtotal_value


class StockPriceFilter(ListFilter):
    """
    Фильтр товаров по цене.
    """
    template = 'admin/warehouse/stock/stock-price-filter.html'
    title = _('По цене')
    parameter_name = 'price'
    request = None

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

        self.request = request
        if 'price_from' in params:
            value = params.pop('price_from')
            self.used_parameters['price_from'] = value

        if 'price_to' in params:
            value = params.pop('price_to')
            self.used_parameters['price_to'] = value

    def has_output(self):
        return True

    def queryset(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get('price_from', None)
        if value_from is not None and value_from != '':
            filters.update({
                'price__gte': self.used_parameters.get('price_from', None),
            })

        value_to = self.used_parameters.get('price_to', None)
        if value_to is not None and value_to != '':
            filters.update({
                'price__lte': self.used_parameters.get('price_to', None),
            })
        return queryset.filter(**filters)

    def value(self):
        return self.used_parameters.get('price_to', None)

    def choices(self, changelist):
        return ({
                    'selected': self.value() is not None,
                    'request': self.request,
                    'form': StockPriceFilterForm(data={
                        'price_from': self.used_parameters.get('price_from',
                                                               None),
                        'price_to': self.used_parameters.get('price_to',
                                                             None),
                    }),
                },)


class StockCategoryFilter(TreeRelatedFieldListFilter):
    """
    Фильтр товаров по категории.
    """
    template = 'admin/warehouse/stock/stock-total-value.html'
    mptt_level_indent = 20

    def field_choices(self, field, request, model_admin):
        mptt_level_indent = self.mptt_level_indent
        initial_choices = field.get_choices(include_blank=False)
        pks = [pk for pk, val in initial_choices]
        models = field.related_model._default_manager.filter(pk__in=pks)
        levels_dict = {model.pk: getattr(model, model._mptt_meta.level_attr)
                       for model in models}
        subcategories = {model.pk: model.get_descendant_count()
                         for model in models}
        choices = []
        for pk, val in initial_choices:
            padding_style = ' style="padding-%s:%spx"' % (
                'left',
                mptt_level_indent * levels_dict[pk],)
            choices.append((pk, val + f'({subcategories[pk]})',
                           mark_safe(padding_style)))
        return choices

    def total_value(self, obj_id):
        if obj_id is not None:
            obj = Category.objects.filter(id=obj_id).get()
        else:
            obj = None
        return subtotal_value(obj)

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None and not self.lookup_val_isnull,
            'query_string': cl.get_query_string({},
                                                [self.changed_lookup_kwarg,
                                                 self.lookup_kwarg_isnull]),
            'display': _('All'),
            'total_cost': self.total_value(self.lookup_val)
        }
        for pk_val, val, padding_style in self.lookup_choices:
            yield {
                'selected': self.lookup_val == str(pk_val),
                'query_string': cl.get_query_string({
                    self.changed_lookup_kwarg: pk_val,
                }, [self.lookup_kwarg_isnull]),
                'display': val,
                'padding_style': padding_style,
            }


class StockEmptyFilter(SimpleListFilter):
    """
    Фильтр товаров по наличию/отсутствию.
    """
    title = _('По наличию')
    parameter_name = 'number'

    def lookups(self, request, model_admin):
        return (
            ('Empty', _('Нет на складе')),
            ('Available', _('Есть на складе'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'Available':
            return queryset.filter(number__gt=0)
        if self.value() == 'Empty':
            return queryset.filter(number__exact=0)
