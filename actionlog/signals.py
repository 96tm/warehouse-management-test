from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from cargo.models import Cargo
from customer.models import Customer
from supplier.models import Supplier
from shipment.models import Shipment
from .models import ModelChangeLogsModel
from common.models import ShipmentStock, CargoStock

from django.utils.translation import gettext as _


@receiver([post_save, post_delete], sender=Shipment)
@receiver([post_save, post_delete], sender=ShipmentStock)
@receiver([post_save, post_delete], sender=Customer)
@receiver([post_save, post_delete], sender=Supplier)
@receiver([post_save, post_delete], sender=Cargo)
def save_del_data(sender, instance, created=None, **kwargs):
    log = ModelChangeLogsModel(table_name=instance._meta.db_table,
                               data=str(instance))
    if created:
        log.action = _('создание')
    elif created == False:
        log.action = _('редактирование')
    else:
        log.action = _('удаление')
    log.save()


@receiver([post_save, post_delete], sender=CargoStock)
def save_del_CargoStock(sender, instance, created=None, **kwargs):
    supplier = str(instance.cargo.supplier.organization)
    log = ModelChangeLogsModel(table_name=str(sender._meta.verbose_name),
                               data='№_поставки: ' + str(instance.cargo_id)
                                    + ', поставщик: ' + supplier
                                    + ', артикул: ' + str(instance.stock_id)
                                    + ', количество: ' + str(instance.number))
    if created:
        log.action = _('создание')
    elif created == False:
        log.action = _('редактирование')
    else:
        log.action = _('удаление')
    log.save()
