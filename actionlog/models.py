from django.db import models

from django.utils.translation import gettext as _

# Create your models here.


class ModelChangeLogsModel(models.Model):
    class Meta:
        verbose_name = _('Операция')
        verbose_name_plural = _('История операций')
    table_name = models.CharField(max_length=132, null=False, blank=True,
                                  verbose_name=_('Тип объекта'))
    data = models.TextField(null=False, blank=True,
                            verbose_name=_('Объект'))
    action = models.CharField(max_length=16, null=False, blank=True,
                              verbose_name=_('Действие'))
    date = models.DateTimeField(auto_now_add=True,
                                verbose_name='Дата')

    def __str__(self):
        return _('операция - ') + self.action
