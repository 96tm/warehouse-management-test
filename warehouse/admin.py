import pytz
import qrcode
import io
import uuid

from django import forms
from django.contrib import admin
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _
from django.db.models import Sum
from django.core.mail import EmailMessage

from email.mime.base import MIMEBase
from email.encoders import encode_base64

from .models import Supplier, Customer, Stock, Category
from .models import Shipment, ShipmentStock


# функция gettext с псевдонимом _ применяется к строками
# для последующего перевода

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = []

    # дополнительные поля для формы
    number_of_items = forms.CharField(max_length=10,
                                      label=_('Количество товаров'))
    total = forms.CharField(max_length=10, label=_('Сумма покупки'))
    customer_name = forms.CharField(max_length=80, label=_('Покупатель'))
    shipment_id = forms.CharField(max_length=10, label=_('Номер заказа'))
    shipment_date = forms.CharField(max_length=19, label=_('Дата заказа'))
    shipment_status = forms.CharField(max_length=9, label=_('Статус заказа'))
    shipment_qr = forms.CharField(max_length=50, label=_('Код подтверждения'))

    field_order = ['number_of_items', 'total', 'customer_name',
                   'shipment_id', 'shipment_date',
                   'shipment_status', 'shipment_qr']

    # добавляем инициализацию дополнительных полей при создании формы
    def __init__(self, *args, **kwargs):
        super(ShipmentForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs.get('instance'):
            current_shipment = kwargs['instance']
            for key, value in self.fields.items():
                value.widget = forms.TextInput({'size': '35',
                                                'readonly': 'readonly'})
                value.required = False
            # выбираем записи из many-to-many таблицы shipmentstock,
            # относящиеся к выбранной погрузке,
            # к каждой записи добавляем цену соответствующего товара из stocks
            shipment_stocks = (ShipmentStock
                               .objects.select_related('stock')
                               .filter(shipment=current_shipment))
            # сумма погрузки
            money = sum([shipment_stock.stock.price * shipment_stock.number
                         for shipment_stock in shipment_stocks])
            # общее количество всех товаров погрузки
            number = (ShipmentStock.objects
                      .filter(shipment=current_shipment)
                      .aggregate(Sum('number')))['number__sum']
            date = (current_shipment.date
                    .astimezone(tz=pytz.timezone(settings.TIME_ZONE))
                    .strftime('%Y-%m-%d %H:%M:%S'))
            values = (number, money, current_shipment.customer.full_name,
                      current_shipment.id, date, current_shipment.status,
                      current_shipment.qr)
            for index, field_name in enumerate(self.field_order):
                self.fields[field_name].initial = values[index]


class CustomerAdmin(admin.ModelAdmin):
    # объект для отображения заказов выбранного покупателя
    class ShipmentInline(admin.StackedInline):
        form = ShipmentForm
        model = Shipment
        can_delete = False
        min_num = 0
        max_num = 0
        verbose_name = _("Покупка")
        verbose_name_plural = _("Покупки")
        show_change_link = True

    inlines = [ShipmentInline, ]
    fieldsets = (
        (_('ДАННЫЕ ПОКУПАТЕЛЯ'),
         {'fields': ('full_name', 'phone_number',
                     'email', 'contact_info')}),
    )


class ShipmentAdmin(admin.ModelAdmin):
    form = ShipmentForm
    # поля для отображения в списке погрузок
    list_display = ['date', 'customer', 'status', 'qr', ]
    # поля для фильтрации
    list_filter = ['date', 'customer', 'status', ]
    # поля для текстового поиска
    search_fields = ['status', 'customer__full_name', ]
    # поля формы изменения погрузки
    fields = ['shipment_id', 'customer_name', 'number_of_items',
              'total', 'shipment_status', 'shipment_date', 'shipment_qr', ]

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
                                                      form_url='',
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


admin.site.register(Supplier)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Stock)
admin.site.register(Category)
admin.site.register(Shipment, ShipmentAdmin)
