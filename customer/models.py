from django.db import models

from django.utils.translation import gettext as _


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
