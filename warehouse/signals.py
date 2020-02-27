from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Shipment, ShipmentStock, Customer, ModelChangeLogsModel
from .models import Supplier, Cargo, CategoryMPTT, CargoStock

from datetime import datetime

@receiver([post_save, post_delete], sender=CategoryMPTT)
@receiver([post_save, post_delete], sender=Shipment)
@receiver([post_save, post_delete], sender=ShipmentStock)
@receiver([post_save, post_delete], sender=Customer)
@receiver([post_save, post_delete], sender=Supplier)
@receiver([post_save, post_delete], sender=Cargo)
def save_del_data(sender, instance, created=None, **kwargs):
    log = ModelChangeLogsModel(table_name=str(sender._meta.verbose_name),
                               data=str(instance))
    if created:
        log.action = 'создание'
    elif created == False:
        log.action = 'изменение'
    else:
        log.action = 'удаление'
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
        log.action = 'создание'
    elif created == False:
        log.action = 'изменение'
    else:
        log.action = 'удаление'
    log.save()
