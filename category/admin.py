from django.contrib import admin
from .models import Category
from mptt.admin import DraggableMPTTAdmin
from common.models import subtotal_value
from django.utils.translation import gettext as _


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    """
    Отображение списка категорий.
    """
    tree_auto_open = True
    # mptt_level_indent = 30
    mptt_indent_field = 'name'
    list_display = ('tree_actions', 'id', 'indented_title',
                    'num_of_subcategory', 'total_value', )
    list_display_links = ('indented_title', )
    search_fields = ('name', )

    def num_of_subcategory(self, obj):
        return obj.get_children().count()

    def total_value(self, obj):
        return subtotal_value(obj)

    num_of_subcategory.short_description = _('Количество подкатегорий')
    total_value.short_description = _('Общая стоимость')
