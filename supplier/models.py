from django.db import models

from django.utils.translation import gettext as _


class Supplier(models.Model):
    """
    Таблица поставщиков.
    """
    class Meta:
        verbose_name = _('Поставщик')
        verbose_name_plural = _('Поставщики')

    organization = models.CharField(max_length=80, unique=True,
                                    verbose_name=_('Организация'))
    address = models.TextField(verbose_name=_('Адрес'))
    phone_number = models.CharField(max_length=20, verbose_name=_('Телефон'))
    email = models.EmailField(verbose_name=_('Электронная почта'))
    legal_details = models.TextField(verbose_name=_('Реквизиты'))
    contact_info = models.TextField(null=True,
                                    verbose_name=_('Контактная информация'))
    categories = models.ManyToManyField('category.Category',
                                        through='common.SupplierCategory')

    def __str__(self):
        return self.organization
