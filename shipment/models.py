from django.db import models

from django.utils.translation import gettext as _

from common.models import format_date


def get_shipment_total(obj):
    return sum([row.stock.price * row.number
                for row in obj.shipmentstock_set.all()])


class Shipment(models.Model):
    """
    Таблица покупок.
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

    customer = models.ForeignKey('customer.Customer',
                                 on_delete=models.CASCADE,
                                 verbose_name=_('Покупатель'))
    status = models.CharField(max_length=9, choices=choices,
                              verbose_name=_('Статус покупки'),
                              default=CREATED)
    date = models.DateTimeField(auto_now_add=True,
                                verbose_name=_('Дата покупки'))
    qr = models.TextField(null=True, verbose_name=_('Код подтверждения'))
    stocks = models.ManyToManyField('warehouse.Stock',
                                    through='common.ShipmentStock')

    def __str__(self):
        return (format_date(self.date) + ', '
                + str(self.customer) + ', ' + self.status.lower())
