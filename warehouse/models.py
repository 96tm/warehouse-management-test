import pytz

from django.db import models

from django.conf import settings

from django.utils.translation import gettext as _


def format_date(date):
    """
    Форматировать дату, полученную из базы данных,
    в установленный часовой пояс
    :param date: полученная дата типа date
    :return: str: строковое представление даты
    """
    return (date
            .astimezone(tz=pytz.timezone(settings.TIME_ZONE))
            .strftime('%Y-%m-%d %H:%M:%S'))


def get_parent_name(obj):
    if not obj.parent_id:
        return _('Нет базовой категории')
    else:
        return Category.objects.get(pk=obj.parent_id).name


def get_cargo_total(obj):
    return sum([row.stock.price * row.number
                for row in obj.cargostock_set.all()])


def get_shipment_total(obj):
    return sum([row.stock.price * row.number
                for row in obj.shipmentstock_set.all()])


def get_parent_categories(category_pk):
    """
    Получить список доступных для выбора базовых категорий
    :param category_pk:первичный ключ категории
    :return: list: список кортежей вида (pk, name)
    """
    categories = (Category.objects.exclude(pk=category_pk).values('parent_id',
                                                                  'pk',
                                                                  'name'))
    categories_list = sorted(categories, key=lambda x: x['parent_id'])
    to_remove = [category_pk, ]
    choices = [(0, _('Нет базовой категории')), ]
    for category in categories_list:
        print(category, 'to remove', to_remove)
        if category['parent_id'] not in to_remove:
            choices.append((category['pk'], category['name']))
        else:
            to_remove.append(category['pk'])
    return choices


class Category(models.Model):
    """
    Таблица категорий товаров
    """
    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        unique_together = (('name', 'parent_id'), )

    name = models.CharField(max_length=80,
                            blank=False, verbose_name=_('Категория'))
    parent_id = models.IntegerField(default=0,
                                    verbose_name=_('Базовая категория'))

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """
    Таблица поставщиков
    """
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
    categories = models.ManyToManyField(Category, through='SupplierCategory')

    def __str__(self):
        return self.organization


class Customer(models.Model):
    """
    Таблица покупателей
    """
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
    """
    Таблица товаров (склад)
    """
    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')

    article = models.IntegerField(primary_key=True,
                                  verbose_name=_('Артикул'))
    name = models.CharField(max_length=80,
                            verbose_name=_('Наименование'))
    price = models.FloatField(verbose_name=_('Цена'))
    number = models.IntegerField(verbose_name=_('Количество на складе'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name=_('Категория'))

    def __str__(self):
        return self.name


class Shipment(models.Model):
    """
    Таблица покупок
    """
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
        return (format_date(self.date) + ', '
                + str(self.customer) + ', ' + self.status.lower())


class Cargo(models.Model):
    """
    Таблица поставок
    """
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
        return (str(self.pk) + ', ' + str(self.supplier) + ', '
                + self.status + ', ' + str(format_date(self.date)))


class CargoDetails(models.Model):
    """
    Таблица для оформления нескольки товаров в поставку
    """
    order_number = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    quantity = models.SmallIntegerField(default=1)

    def __str__(self):
        return (str(self.order_number.pk) + ', ' + str(self.name) + ', '
                + str(self.quantity))


class ShipmentStock(models.Model):
    """
    Таблица многие-ко-многим покупка-товар
    """
    class Meta:
        unique_together = (("shipment", "stock"),)
        verbose_name = _('Покупка')
        verbose_name_plural = _('Покупки')

    shipment = models.ForeignKey(Shipment,
                                 on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock,
                              on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name=_('Количество'))

    def __str__(self):
        return _('покупатель - ') + self.shipment.customer.full_name


class CargoStock(models.Model):
    """
    Таблица многие-ко-многим поставка-товар
    """
    class Meta:
        unique_together = (("cargo", "stock"),)
        verbose_name = _('Поставка')
        verbose_name_plural = _('Поставки')

    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name=_('Количество'))

    def __str__(self):
        return _('поставщик - ') + self.cargo.supplier.organization


class SupplierCategory(models.Model):
    """
    Таблица многие-ко-многим поставщик-категория
    """
    class Meta:
        unique_together = (('supplier', 'category'), )
        verbose_name = _('Категория поставщиков')
        verbose_name_plural = _('Категории поставщиков')

    supplier = models.ForeignKey(Supplier,
                                 on_delete=models.CASCADE)
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE)

    def __str__(self):
        return _('поставщик - ') + self.supplier.organization
