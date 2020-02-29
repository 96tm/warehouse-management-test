from django.db import models

from django.utils.translation import gettext as _

from mptt.models import TreeForeignKey


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
    category = TreeForeignKey('category.Category', on_delete=models.CASCADE,
                              verbose_name=_('Категория'))

    def __str__(self):
        return self.name
