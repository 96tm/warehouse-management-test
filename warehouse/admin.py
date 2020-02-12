import qrcode
import io
import uuid

from django.contrib import admin

from django.urls import reverse
from django.utils.translation import gettext as _

from django.core.mail import EmailMessage


from email.mime.base import MIMEBase
from email.encoders import encode_base64

from .models import Supplier, Customer, Stock, Category, CargoDetails
from .models import Shipment, ShipmentStock, Cargo, CargoStock

from .forms import CustomerForm, SupplierForm
from .forms import ShipmentForm, CargoForm, StockFormM2M


# функция gettext с псевдонимом _ применяется к строками
# для последующего перевода


class CargoAdmin(admin.ModelAdmin):
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
    list_display = ['supplier', 'date', 'status', ]
    # поля для фильтрации
    list_filter = ['date', 'supplier', 'status', ]
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


class SupplierAdmin(admin.ModelAdmin):
    class CargoInline(admin.StackedInline):
        model = Cargo
        form = CargoForm
        min_num = 0
        max_num = 0
        can_delete = False
        show_change_link = True

    form = SupplierForm
    inlines = [CargoInline, ]
    list_display = ['organization', 'email', 'phone_number', 'address', ]
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


class CustomerAdmin(admin.ModelAdmin):
    # объект для отображения заказов выбранного покупателя
    class ShipmentInline(admin.StackedInline):
        form = ShipmentForm
        model = Shipment
        min_num = 0
        max_num = 0
        verbose_name = _("Покупка")
        verbose_name_plural = _("Покупки")
        can_delete = False
        show_change_link = True

    form = CustomerForm
    list_display = ['full_name', 'email', 'phone_number']
    inlines = [ShipmentInline, ]
    fieldsets = (
        (_('ДАННЫЕ ПОКУПАТЕЛЯ'),
         {'fields': ('full_name', 'phone_number',
                     'email', 'contact_info')}),
    )


class ShipmentAdmin(admin.ModelAdmin):
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
    list_display = ['customer', 'date', 'status', 'qr', ]
    # поля для фильтрации
    list_filter = ['date', 'customer', 'status', ]
    # поля для текстового поиска
    search_fields = ['status', 'customer__full_name', ]
    # поля формы изменения погрузки
    fieldsets = ((_('ИНФОРМАЦИЯ О ПОКУПКЕ'),
                  {'fields': ('shipment_id', 'customer_name',
                              'number_of_items', 'total',
                              'shipment_status', 'shipment_date',
                              'shipment_qr', )}), )

    inlines = [StockInline, ]

    # убираем кнопку "Добавить погрузку" при отображении списка погрузок
    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        # нажата кнопка Cancel
        if '_cancel' in request.POST:
            obj.status = Shipment.CANCELLED
        elif obj.status == Shipment.CREATED:
            obj.status = Shipment.SENT
            obj.qr = str(obj.id) + str(uuid.uuid4())
            email = obj.customer.email
            link = self.get_confirmation_link(request.get_host())
            body = _('Здравствуйте, подтвердите '
                     + 'получение покупки: перейдите по ссылке ')
            body += link + _(' и введите номер из QR-кода во вложении.')
            self.send_email_to_customer(email, body, obj)
        elif obj.status == Shipment.SENT:
            obj.status = Shipment.DONE
        super(ShipmentAdmin, self).save_model(request, obj, form, change)

    # добавляем значения в extra_context для дальнейшего использования
    # на странице формы информации о погрузке
    def change_view(self, request, object_id,
                    form_url='', extra_context=None):
        extra = extra_context or {}
        extra['STATUS_VALUE'] = Shipment.objects.get(pk=object_id).status
        extra['STATUS_DONE'] = Shipment.DONE
        extra['STATUS_CANCELLED'] = Shipment.CANCELLED
        extra['STATUS_CREATED'] = Shipment.CREATED
        extra['STATUS_SENT'] = Shipment.SENT
        return super(ShipmentAdmin, self).change_view(request, object_id,
                                                      form_url,
                                                      extra_context=extra)

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


admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Stock)
admin.site.register(Category)
#admin.site.register(CargoDetails)
admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(Cargo, CargoAdmin)
