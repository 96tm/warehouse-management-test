import pytz

from django.db import models

from django.conf import settings

from django.utils.translation import gettext as _

from warehouse.models import Stock


def subtotal_value(obj):
    """
    Подсчет стоимости товаров подкатегорий
    """
    result = 0
    if obj is not None:
        values = (Stock
                  .objects
                  .filter(category__in=obj.get_descendants(include_self=True))
                  .values_list('price', 'number'))
    else:
        values = Stock.objects.all().values_list('price', 'number')
    for price, count in values:
        result += price * count
    return result


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


class ShipmentStock(models.Model):
    """
    Таблица многие-ко-многим покупка-товар
    """
    class Meta:
        unique_together = (("shipment", "stock"),)
        verbose_name = _('Покупка')
        verbose_name_plural = _('Покупки')

    shipment = models.ForeignKey('shipment.Shipment',
                                 on_delete=models.CASCADE)
    stock = models.ForeignKey('warehouse.Stock',
                              on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name=_('Количество'))

    def __str__(self):
        return _('покупатель - ') + self.shipment.customer.full_name


class CargoStock(models.Model):
    """
    Таблица многие-ко-многим поставка-товар
    """
    class Meta:
        constraints = [models.UniqueConstraint(fields=['cargo', 'stock'],
                                               name='cargo_stock_unique')]
        verbose_name = _('Поставка')
        verbose_name_plural = _('Поставки')

    cargo = models.ForeignKey('cargo.Cargo', on_delete=models.CASCADE)
    stock = models.ForeignKey('warehouse.Stock', on_delete=models.CASCADE)
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

    supplier = models.ForeignKey('supplier.Supplier',
                                 on_delete=models.CASCADE)
    category = models.ForeignKey('category.Category',
                                 on_delete=models.CASCADE)

    def __str__(self):
        return _('поставщик - ') + self.supplier.organization
