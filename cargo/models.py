from django.db import models

from django.utils.translation import gettext as _

from common.models import format_date


def get_cargo_total(obj):
    return sum([row.stock.price * row.number
                for row in obj.cargostock_set.all()])


class Cargo(models.Model):
    """
    Таблица поставок.
    """
    class Meta:
        verbose_name = _('Поставка')
        verbose_name_plural = _('Поставки')

    DONE = 'Исполнено'
    IN_TRANSIT = 'В пути'
    choices = [(DONE, DONE), (IN_TRANSIT, IN_TRANSIT)]
    supplier = models.ForeignKey('supplier.Supplier',
                                 on_delete=models.CASCADE,
                                 verbose_name=_('Поставщик'))
    status = models.CharField(max_length=10, choices=choices,
                              verbose_name=_('Статус'),
                              default=IN_TRANSIT)
    date = models.DateTimeField(auto_now_add=True,
                                verbose_name=_('Дата поставки'))
    stocks = models.ManyToManyField('warehouse.Stock',
                                    through='common.CargoStock',
                                    verbose_name=_('Товары'))

    def __str__(self):
        return (str(self.pk) + ', ' + str(self.supplier) + ', '
                + self.status + ', ' + str(format_date(self.date)))


class CargoDetails(models.Model):
    """
    Таблица для оформления нескольки товаров в поставку.
    """
    order_number = models.ForeignKey('cargo.Cargo', on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    quantity = models.SmallIntegerField(default=1)

    def __str__(self):
        return (str(self.order_number.pk) + ', ' + str(self.name) + ', '
                + str(self.quantity))
