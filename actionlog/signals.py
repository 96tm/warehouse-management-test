from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from cargo.models import Cargo
from customer.models import Customer
from supplier.models import Supplier
from shipment.models import Shipment
from .models import LogModel

from django.utils.translation import gettext as _


@receiver([post_save, post_delete], sender=Shipment)
@receiver([post_save, post_delete], sender=Customer)
@receiver([post_save, post_delete], sender=Supplier)
@receiver([post_save, post_delete], sender=Cargo)
def save_del_data(sender, instance, created=None, **kwargs):
    table_name = instance.__class__._meta.verbose_name
    log = LogModel(table_name=table_name, data=str(instance),
                   object_entry_id=instance.pk)
    if created:
        log.action = _('Создание')
    elif created == False:
        log.action = _('Редактирование')
    else:
        log.action = _('Удаление')
    log.save()
