from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Shipment, ShipmentStock, Customer, ModelChangeLogsModel
from .models import Supplier, Cargo, Category, CargoStock


@receiver([post_delete], sender=Category)
def delete_category_callback(sender, **kwargs):
    """
    :param sender: класс Category
    :param kwargs: instance - удаленная категория
    :return: None
    """
    instance = kwargs['instance']
    for category in sender.objects.all():
        if category.parent_id == instance.parent_id:
            category.parent_id = 0
            category.save()


@receiver([post_save, post_delete], sender=Shipment)
@receiver([post_save, post_delete], sender=ShipmentStock)
@receiver([post_save, post_delete], sender=Customer)
@receiver([post_save, post_delete], sender=Supplier)
@receiver([post_save, post_delete], sender=Cargo)
def save_del_data(sender, instance, created=None, **kwargs):
    log = ModelChangeLogsModel(table_name=instance._meta.db_table,
                               data=str(instance))
    if created:
        log.action = 'create'
    elif created == False:
        log.action = 'update'
    else:
        log.action = 'delete'
    log.save()


@receiver([post_save, post_delete], sender=CargoStock)
def save_del_CargoStock(sender, instance, created=None, **kwargs):
    supplier = str(instance.cargo.supplier.organization)
    log = ModelChangeLogsModel(table_name=instance._meta.db_table,
                               data='№_поставки: ' + str(instance.cargo_id)
                                    + ', поставщик: ' + supplier
                                    + ', артикул: ' + str(instance.stock_id)
                                    + ', количество: ' + str(instance.number))
    if created:
        log.action = 'create'
    elif created == False:
        log.action = 'update'
    else:
        log.action = 'delete'
    log.save()
