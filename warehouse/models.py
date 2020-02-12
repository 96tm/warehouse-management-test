from django.core.validators import MinValueValidator
from django.db import models
import uuid
from django.db.models import ManyToManyField
from django.conf import settings
from django.utils.translation import gettext as _
import pytz


class Category(models.Model):
    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    name = models.CharField(max_length=80)
    parent_id = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    class Meta:
        verbose_name = _('Поставщик')
        verbose_name_plural = _('Поставщики')

    organization = models.CharField(max_length=80,
                                    verbose_name=_('Организация'))
    address = models.TextField(verbose_name=_('Адрес'))
    phone_number = models.CharField(max_length=20, verbose_name=_('Телефон'))
    email = models.EmailField(verbose_name=_('Электронная почта'))
    legal_details = models.TextField(verbose_name=_('Реквизиты'))
    contact_info = models.TextField(null=True,
                                    verbose_name=_('Контактная информация'))
    categories = models.ManyToManyField(Category, through='SupplierCategory',
                                        related_name='suppliers')
    #objects = models.Manager()

    def __str__(self):
        return self.organization


class Customer(models.Model):
    class Meta:
        verbose_name = _('Покупатель')
        verbose_name_plural = _('Покупатели')

    full_name = models.CharField(max_length=80, verbose_name=_('ФИО'))
    phone_number = models.CharField(max_length=20, verbose_name=_('Телефон'))
    email = models.EmailField(verbose_name=_('Электронная почта'))
    contact_info = models.TextField(null=True,
                                    verbose_name=_('Контактные данные'))

    def __str__(self):
        return self.full_name


class Stock(models.Model):
    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')

    article = models.IntegerField(primary_key=True,
                                  verbose_name=_('Артикул'))
    name = models.CharField(max_length=80,
                            verbose_name=_('Наименование'))
    price = models.FloatField(verbose_name=_('Цена'))
    number = models.IntegerField(verbose_name=_('Количество на складе'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, verbose_name=_('Категория'))

    def __str__(self):
        return self.name


class Shipment(models.Model):
    class Meta:
        verbose_name = _('Покупка')
        verbose_name_plural = _('Покупки')

    DONE = 'Исполнено'
    CREATED = 'Проверка'
    SENT = 'Собрано'
    CANCELLED = 'Отменено'
    choices = [(DONE, DONE), (CREATED, CREATED),
               (SENT, SENT), (CANCELLED, CANCELLED), ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 verbose_name=_('Покупатель'))
    status = models.CharField(max_length=9, choices=choices,
                              verbose_name=_('Статус покупки'),
                              default=CREATED)
    date = models.DateTimeField(auto_now_add=True,
                                verbose_name=_('Дата покупки'))
    qr = models.TextField(null=True, verbose_name=_('Код подтверждения'))
    stocks = models.ManyToManyField(Stock, through='ShipmentStock')

    def __str__(self):
        date = self.date.astimezone(tz=pytz.timezone(settings.TIME_ZONE))
        date = date.strftime('%Y-%m-%d %H:%M:%S')
        return date + ', ' + str(self.customer) + ', ' + self.status.lower()


class Cargo(models.Model):
    class Meta:
        verbose_name = _('Поставка')
        verbose_name_plural = _('Поставки')

    DONE = 'Исполнено'
    IN_TRANSIT = 'В пути'
    choices = [(DONE, DONE), (IN_TRANSIT, IN_TRANSIT)]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,
                                 verbose_name=_('Поставщик'))
    status = models.CharField(max_length=10, choices=choices,
                              verbose_name=_('Статус'),
                              default=IN_TRANSIT)
    date = models.DateTimeField(auto_now_add=True,
                                verbose_name=_('Дата поставки'))
    stocks = models.ManyToManyField(Stock, through='CargoStock',
                                    verbose_name=_('Товары'))

    def __str__(self):
        return str(self.pk) + ', ' + str(self.supplier) + ', ' + self.status + ', ' + str(self.date)


class CargoDetails(models.Model):
    order_number = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    quantity = models.SmallIntegerField(default=1)

    def __str__(self):
        return str(self.order_number.pk) + ', ' + str(self.name) + ', ' + str(self.quantity)


class ShipmentStock(models.Model):
    class Meta:
        unique_together = (("shipment", "stock"),)

    shipment = models.ForeignKey(Shipment,
                                 on_delete=models.SET_NULL, null=True)
    stock = models.ForeignKey(Stock,
                              on_delete=models.SET_NULL,
                              null=True)
    number = models.IntegerField(verbose_name=_('Количество'))

    def __str__(self):
        return self.stock.name


class CargoStock(models.Model):
    class Meta:
        unique_together = (("cargo", "stock"),)

    cargo = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True)
    number = models.IntegerField(verbose_name=_('Количество'))

    def __str__(self):
        return self.stock.name


class SupplierCategory(models.Model):
    class Meta:
        unique_together = (('supplier', 'category'),)
        verbose_name = _('supplier_category')
        verbose_name_plural = _('supplier_categories')

    supplier = models.ForeignKey(Supplier,
                                 on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE, null=True)
