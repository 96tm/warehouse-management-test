from django.contrib import admin

from django.utils.translation import gettext as _

from .models import Stock

from .filters import StockCategoryFilter, StockEmptyFilter
from .filters import StockPriceFilter


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Отображение списка товаров.
    """
    list_display = ('article', 'name', 'price', 'number', 'category',)
    list_display_links = ('name',)
    search_fields = ('article', 'name',)
    ordering = ('category', 'name',)
    list_per_page = 25
    verbose_name = _('Товар')
    verbose_name_plural = _('Товары')
    list_filter = (StockPriceFilter, ('category', StockCategoryFilter),
                   StockEmptyFilter)


admin.site.site_header = _('Администрирование склада')
