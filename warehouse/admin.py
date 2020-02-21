import qrcode
import io
import uuid

from django.urls import reverse
from django.contrib import admin, messages
from django.db.models import Q
from django.core.mail import EmailMessage
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from django.contrib.admin import ListFilter, SimpleListFilter
from django.utils.translation import gettext as _

from .forms import CustomerForm, SupplierForm
from .forms import StockPriceFilterForm, CategoryForm
from .forms import ShipmentForm, CargoForm, StockFormM2M

from .models import get_shipment_total
from .models import Cargo, CargoStock
from .models import Supplier, Customer, Stock, Category
from .models import Shipment, ShipmentStock, ModelChangeLogsModel

# функция gettext с псевдонимом _ применяется к строками
# для последующего перевода


def subtotal_value(obj_id):
    results = Category.objects.filter(parent_id=obj_id).values('id')
    total = 0
    if results:
        for result in results:
            total += subtotal_value(result['id'])
    else:
        results = Stock.objects.filter(category__id=obj_id).values('price',
                                                                   'number')
        for result in results:
            total += result['price'] * result['number']
    return total


class StockPriceFilter(ListFilter):
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


class StockCategoryFilter(SimpleListFilter):
    template = 'admin/warehouse/stock/stock-total-value.html'
    title = _('По категории')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        def subcategories(obj_id=0, sublevel='', name=_('Все товары')):
            num_of_subcategory = (Category
                                  .objects.filter(parent_id=obj_id).count())
            total = [(obj_id, (sublevel + name + f'({num_of_subcategory})'))]
            results = (Category
                       .objects.filter(parent_id=obj_id).values('id', 'name'))
            if results:
                sublevel += ' - '
                for result in results:
                    total += subcategories(result['id'],
                                           sublevel, result['name'])
            return total

        results = subcategories()
        return results

    def queryset(self, request, queryset):
        if self.value() is not None:
            a = int(self.value())
            if a != 0:
                def have_subcategory(obj_id):
                    total = [obj_id]
                    results = (Category
                               .objects.filter(parent_id=obj_id).values('id'))
                    if results:
                        for result in results:
                            total += have_subcategory(result['id'])
                    return total

                results = have_subcategory(a)
                subresult = Q()
                for result in results:
                    subresult = subresult | Q(category__id=result)
                queryset = queryset.filter(subresult)
        return queryset

    def total_value(self, obj_id):
        return subtotal_value(obj_id)

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            query = changelist.get_query_string({self.parameter_name: lookup})
            yield {
                'selected': self.value() == str(lookup),
                'query_string': query,
                'display': title,
                'total_cost': self.total_value(self.value())
            }


class StockEmptyFilter(SimpleListFilter):
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


@admin.register(ModelChangeLogsModel)
class LogAdmin(admin.ModelAdmin):
    model = ModelChangeLogsModel
    list_display = ('date', 'table_name', 'action', 'data')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Отображение списка и формы товаров
    """
    list_display = ('article', 'name', 'price', 'number', 'category', )
    list_display_links = ('name', )
    list_filter = (StockPriceFilter, StockCategoryFilter, StockEmptyFilter)
    search_fields = ('article', 'name', )
    ordering = ('category', 'name', )
    list_per_page = 25
    verbose_name = _('Товар')
    verbose_name_plural = _('Товары')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Отображение списка и формы категорий
    """
    form = CategoryForm
    list_display = ('id', 'name', 'upper_categories', 'lower_categories',
                    'parent_id', 'num_of_subcategory', 'total_value', )
    ordering = ('parent_id', 'id', )
    fields = ('name', 'parent_name', )

    def save_model(self, request, obj, form, change):
        obj.parent_id = form.cleaned_data['parent_name']
        super().save_model(request, obj, form, change)

    def parent_name(self, obj):
        if not obj.parent_id:
            return _('Нет базовой категории')
        else:
            return Category.objects.get(pk=obj.parent_id).name

    def upper_categories(self, obj):
        next_id = obj.parent_id
        result = ''  # str(obj.name)
        while next_id != 0:
            next_id = Category.objects.get(id=next_id)
            result += '<-' + str(next_id)
            next_id = next_id.parent_id
        return result

    def lower_categories(self, obj):
        obj_id = obj.id
        total = ''
        results = Category.objects.filter(parent_id=obj_id)
        for result in results:
            total += str(result) + ', '
        return total

    def num_of_subcategory(self, obj):
        id = obj.id
        result = Category.objects.filter(parent_id=id).count()
        return result

    def total_value(self, obj):
        obj_id = obj.id
        return subtotal_value(obj_id)

    num_of_subcategory.allow_tags = True
    num_of_subcategory.short_description = _('Количество подкатегорий')
    parent_name.short_description = _('Базовая категория')
    upper_categories.short_description = _('Надкатегории')
    lower_categories.short_description = _('Подкатегории')
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
    list_display = ('supplier', 'date', 'status', )
    # поля для фильтрации
    list_filter = ('date', 'supplier', 'status', )
    # поля для текстового поиска
    search_fields = ['supplier__organization', ]
    fieldsets = ((_('ИНФОРМАЦИЯ О ПОСТАВКЕ'),
                  {'fields': ('cargo_id', 'cargo_supplier',
                              'cargo_status', 'cargo_date',
                              'number', 'total')}), )
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
    list_display = ('organization', 'email', 'phone_number', 'address', )
    fieldsets = ((_('ЮРИДИЧЕСКОЕ ЛИЦО'), {'fields':
                                          ('organization',
                                           'address',
                                           'legal_details', )}),
                 (_('КОНТАКТНЫЕ ДАННЫЕ'), {'fields':
                                           ('contact_info',
                                            'phone_number',
                                            'email', )}),
                 (_('КАТЕГОРИИ ТОВАРОВ'), {'fields':
                                           ('supplier_categories', )}))

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
    list_display = ('full_name', 'email', 'phone_number', )

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
    list_display = ('customer', 'date', 'status', shipment_total, 'qr', )
    # поля для фильтрации
    list_filter = ('date', 'customer', 'status', )
    # поля для текстового поиска
    search_fields = ('status', 'customer__full_name', )
    fieldsets = ((_('ИНФОРМАЦИЯ О ПОКУПКЕ'),
                  {'fields': ('shipment_id', 'customer_name',
                              'number_of_items', 'total',
                              'shipment_status', 'shipment_date',
                              'shipment_qr', )}), )
    inlines = (StockInline, )

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
