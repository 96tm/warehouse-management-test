import qrcode
import io
import uuid

from django.urls import reverse
from django.contrib import admin, messages
from django.contrib.admin import ListFilter, SimpleListFilter
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter
from django.core.mail import EmailMessage
from email.mime.base import MIMEBase
from email.encoders import encode_base64

from django.utils.translation import gettext as _
from django.utils.html import mark_safe

from .forms import CustomerForm, SupplierForm, ModelChangeLogsModelForm
from .forms import StockPriceFilterForm
from .forms import ShipmentForm, CargoForm, StockFormM2M

from .models import get_shipment_total
from .models import Cargo, CargoStock
from .models import Supplier, Customer, Stock, CategoryMPTT
from .models import Shipment, ShipmentStock, ModelChangeLogsModel


# функция gettext с псевдонимом _ применяется к строками
# для последующего перевода


def subtotal_value(obj):
    """
    Подсчет стоимости товаров подкатегорий
    """
    result = 0
    if obj is not None:
        values = Stock.objects.filter(category__in=obj.get_descendants(include_self=True)).values_list('price',
                                                                                                       'number')
    else:
        values = Stock.objects.all().values_list('price', 'number')
    for price, count in values:
        result += price * count
    return result


@admin.register(ModelChangeLogsModel)
class LogAdmin(admin.ModelAdmin):
    """
    Отображение списка вносимых изменений
    """
    form = ModelChangeLogsModelForm
    list_display = ('id', 'table_name', 'data', 'action', 'date',)
    list_display_links = ('table_name',)
    fields = list_display
    list_filter = ('table_name', 'date', 'action',)
    search_fields = ('data',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Отображение списка товаров
    """
    list_display = ('article', 'name', 'price', 'number', 'category',)
    list_display_links = ('name',)
    search_fields = ('article', 'name',)
    ordering = ('category', 'name',)
    list_per_page = 25
    verbose_name = _('Товар')
    verbose_name_plural = _('Товары')

    class StockPriceFilter(ListFilter):
        """
        Фильтр товаров по цене
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
        Фильтр товоров по категории
        """
        template = 'admin/warehouse/stock/stock-total-value.html'
        mptt_level_indent = 20

        def field_choices(self, field, request, model_admin):
            mptt_level_indent = self.mptt_level_indent
            initial_choices = field.get_choices(include_blank=False)
            pks = [pk for pk, val in initial_choices]
            models = field.related_model._default_manager.filter(pk__in=pks)
            levels_dict = {model.pk: getattr(model, model._mptt_meta.level_attr) for model in models}
            subcategories = {model.pk: model.get_descendant_count() for model in models}
            choices = []
            for pk, val in initial_choices:
                padding_style = ' style="padding-%s:%spx"' % (
                    'left',
                    mptt_level_indent * levels_dict[pk],)
                choices.append((pk, val + f'({subcategories[pk]})', mark_safe(padding_style)))
            return choices

        def total_value(self, obj_id):
            if obj_id is not None:
                obj = CategoryMPTT.objects.filter(id=obj_id).get()
            else:
                obj = None
            return subtotal_value(obj)

        def choices(self, cl):
            yield {
                'selected': self.lookup_val is None and not self.lookup_val_isnull,
                'query_string': cl.get_query_string({}, [self.changed_lookup_kwarg, self.lookup_kwarg_isnull]),
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
        Фильтр товоров по наличию/отсутствию
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

    list_filter = (StockPriceFilter, ('category', StockCategoryFilter), StockEmptyFilter)


@admin.register(CategoryMPTT)
class CategoryMPTTAdmin(DraggableMPTTAdmin):
    """
   Отображение списка категорий
   """
    tree_auto_open = True
    # mptt_level_indent = 30
    mptt_indent_field = 'name'
    list_display = ('tree_actions', 'id', 'indented_title', 'num_of_subcategory', 'total_value',)
    list_display_links = ('indented_title',)
    search_fields = ('name',)

    def num_of_subcategory(self, obj):
        return obj.get_children().count()

    def total_value(self, obj):
        return subtotal_value(obj)

    num_of_subcategory.short_description = _('Количество подкатегорий')
    total_value.short_description = _('Общая стоимость')


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    """
    Отображение списка и формы поставок
    """

    class StockInline(admin.StackedInline):
        model = CargoStock
        form = StockFormM2M
        max_num = 0
        min_num = 0
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')
        can_delete = False

    form = CargoForm
    # поля для отображения в списке поставок
    list_display = ('supplier', 'date', 'status',)
    # поля для фильтрации
    list_filter = ('date', 'supplier', 'status',)
    # поля для текстового поиска
    search_fields = ['supplier__organization', ]
    fieldsets = ((_('ИНФОРМАЦИЯ О ПОСТАВКЕ'),
                  {'fields': ('cargo_id', 'cargo_supplier',
                              'cargo_status', 'cargo_date',
                              'number', 'total')}),)
    inlines = [StockInline, ]

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id,
                    form_url='', extra_context=None):
        extra = extra_context or {}
        extra['STATUS_VALUE'] = Cargo.objects.get(pk=object_id).status
        extra['STATUS_IN_TRANSIT'] = Cargo.IN_TRANSIT
        extra['STATUS_DONE'] = Cargo.DONE
        return super().change_view(request, object_id,
                                   form_url,
                                   extra_context=extra)

    def save_model(self, request, obj, form, change):
        if '_confirm' in request.POST and obj.status == Cargo.IN_TRANSIT:
            cargo_stocks = CargoStock.objects.filter(cargo=obj)
            for cs in cargo_stocks:
                cs.stock.number += cs.number
                cs.stock.save()
            obj.status = Cargo.DONE
        super().save_model(request, obj, form, change)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """
    Отображение списка и формы поставщиков
    """

    class CargoInline(admin.StackedInline):
        model = Cargo
        form = CargoForm
        min_num = 0
        max_num = 0
        can_delete = False
        show_change_link = True

    form = SupplierForm
    inlines = [CargoInline, ]
    list_display = ('organization', 'email', 'phone_number', 'address',)
    search_fields = ('organization', 'email', 'phone_number', 'address',)
    fieldsets = ((_('ЮРИДИЧЕСКОЕ ЛИЦО'), {'fields':
                                              ('organization',
                                               'address',
                                               'legal_details',)}),
                 (_('КОНТАКТНЫЕ ДАННЫЕ'), {'fields':
                                               ('contact_info',
                                                'phone_number',
                                                'email',)}),
                 (_('КАТЕГОРИИ ТОВАРОВ'), {'fields':
                                               ('supplier_categories',)}))

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.categories.set(form.cleaned_data['supplier_categories'])

    # не отображаем список записей suppliercategory
    # при подтверждении удаления
    def get_deleted_objects(self, objs, request):
        for obj in objs:
            obj.suppliercategory_set.set([])
        return super().get_deleted_objects(objs, request)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Отображение списка и формы покупателей
    """

    # объект для отображения заказов выбранного покупателя
    class ShipmentInline(admin.StackedInline):
        form = ShipmentForm
        model = Shipment
        can_delete = False
        min_num = 0
        max_num = 0
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        show_change_link = True

    form = CustomerForm
    list_display = ('full_name', 'email', 'phone_number',)
    search_fields = ('full_name', 'email', 'phone_number',)
    inlines = [ShipmentInline, ]

    fieldsets = (
        (_('ДАННЫЕ ПОКУПАТЕЛЯ'),
         {'fields': ('full_name', 'phone_number',
                     'email', 'contact_info')}),
    )


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    """
    Отображение списка и формы заказов
    """

    class StockInline(admin.StackedInline):
        model = ShipmentStock
        form = StockFormM2M
        max_num = 0
        min_num = 0
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')
        can_delete = False

    form = ShipmentForm
    # поля для отображения в списке погрузок
    shipment_total = get_shipment_total
    shipment_total.short_description = _('Сумма покупки')
    list_display = ('customer', 'date', 'status', shipment_total, 'qr',)
    # поля для фильтрации
    list_filter = ('date', 'customer', 'status',)
    # поля для текстового поиска
    search_fields = ('status', 'customer__full_name',)
    fieldsets = ((_('ИНФОРМАЦИЯ О ПОКУПКЕ'),
                  {'fields': ('shipment_id', 'customer_name',
                              'number_of_items', 'total',
                              'shipment_status', 'shipment_date',
                              'shipment_qr',)}),)
    inlines = (StockInline,)

    def is_shipment_available(self, obj):
        return all(s.stock.number > s.number
                   for s in ShipmentStock.objects.filter(shipment=obj))

    # убираем кнопку "Добавить погрузку" при отображении списка погрузок
    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        shipment_available = self.is_shipment_available(obj)
        # нажата кнопка Cancel
        if '_cancel' in request.POST:
            obj.status = Shipment.CANCELLED
        elif obj.status == Shipment.CREATED:
            # проверка данных клиента на сервере
            if shipment_available:
                obj.status = Shipment.SENT
                # обновляем склад
                for shipment_stock in obj.shipmentstock_set.all():
                    shipment_stock.stock.number -= shipment_stock.number
                    shipment_stock.stock.save()
                obj.qr = str(obj.id) + str(uuid.uuid4())
                email = obj.customer.email
                link = self.get_confirmation_link(request.get_host())
                body = _('Здравствуйте, подтвердите '
                         + 'получение покупки: перейдите по ссылке ')
                body += link + _(' и введите номер из QR-кода во вложении.')
                self.send_email_to_customer(email, body, obj)
        elif obj.status == Shipment.SENT:
            obj.status = Shipment.DONE
        super().save_model(request, obj, form, change)
        # печатаем сообщение об ошибке
        if not shipment_available:
            messages.set_level(request, messages.ERROR)
            messages.error(request, _('На складе недостаточно '
                                      + 'товара для данной покупки'))

    # добавляем значения в extra_context для дальнейшего использования
    # на странице формы информации о погрузке
    def change_view(self, request, object_id,
                    form_url='', extra_context=None):
        extra = extra_context or {}
        obj = Shipment.objects.get(pk=object_id)
        extra['STATUS_VALUE'] = Shipment.objects.get(pk=object_id).status
        extra['STATUS_DONE'] = Shipment.DONE
        extra['STATUS_CANCELLED'] = Shipment.CANCELLED
        extra['STATUS_CREATED'] = Shipment.CREATED
        extra['STATUS_SENT'] = Shipment.SENT
        extra['SHIPMENT_AVAILABLE'] = self.is_shipment_available(obj)
        return super().change_view(request, object_id,
                                   form_url, extra_context=extra)

    def get_qr(self, link):
        qr = qrcode.make(link)
        img = qr.get_image()
        byte_stream = io.BytesIO()
        img.save(byte_stream, 'PNG')
        return byte_stream.getvalue()

    def get_confirmation_link(self, host):
        return str(host) + reverse('warehouse:shipment_confirmation')

    def send_email_to_customer(self, receiver, body, customer):
        qr = self.get_qr(customer.qr)
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(qr)
        encode_base64(attachment)
        attachment.add_header('Content-Disposition',
                              'attachment; filename=qr.png')
        message = EmailMessage(subject=_('Подтверждение получения товара'),
                               body=body, to=[receiver, ],
                               attachments=[attachment, ])
        message.send()
