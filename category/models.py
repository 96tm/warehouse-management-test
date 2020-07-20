from django.db import models

from mptt.models import MPTTModel

from mptt.models import TreeForeignKey

from django.utils.translation import gettext as _


class Category(MPTTModel):
    """
    Таблица категорий товаров.
    """
    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        unique_together = (('name', 'parent_id'), )

    name = models.CharField(max_length=80, unique=True,
                            blank=False, verbose_name=_('Название'))
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True, blank=True,
                            related_name='children',
                            verbose_name=_('Надкатегория'))

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = 'name'
