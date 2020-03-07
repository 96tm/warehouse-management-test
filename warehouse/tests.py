from django.test import TestCase
from django.contrib.admin.sites import AdminSite

from .admin import CategoryAdmin
from .models import Category
from .forms import CategoryForm


class MockRequest():
    def __init__(self, *args, **kwargs):
        self.user = kwargs['user']


class MockUser:
    def has_perm(self, perm):
        return True


# Create your tests here.
class CategoryTests(TestCase):
    admin = CategoryAdmin(Category, AdminSite)

    def create_categories(self):
        c0 = Category(name='Бытовая техника')
        request = MockRequest(user=MockUser())
        form = CategoryForm(instance=c0)
        form.cleaned_data = {'parent_name': 0}
        self.admin.save_model(obj=c0, request=request, form=form, change=None)

        c1 = Category(name='Электроника')
        request = MockRequest(user=MockUser())
        form = CategoryForm(instance=c1)
        form.cleaned_data = {'parent_name': 0}
        self.admin.save_model(obj=c1, request=request, form=form, change=None)

        c2 = Category(name='Телевизоры')
        request = MockRequest(user=MockUser())
        form = CategoryForm(instance=c2)
        form.cleaned_data = {'parent_name': c1.pk}
        self.admin.save_model(obj=c2, request=request, form=form, change=None)

        c3 = Category(name='Телефоны')
        form = CategoryForm(instance=c3)
        form.cleaned_data = {'parent_name': c1.pk}
        self.admin.save_model(obj=c3, request=request, form=form, change=None)

        c4 = Category(name='ЖК телевизоры')
        form = CategoryForm(instance=c4)
        form.cleaned_data = {'parent_name': c2.pk}
        self.admin.save_model(obj=c4, request=request, form=form, change=None)

        c5 = Category(name='Full HD телевизоры')
        form = CategoryForm(instance=c5)
        form.cleaned_data = {'parent_name': c4.pk}
        self.admin.save_model(obj=c5, request=request, form=form, change=None)

        c6 = Category(name='Холодильники')
        form = CategoryForm(instance=c6)
        form.cleaned_data = {'parent_name': c0.pk}
        self.admin.save_model(obj=c6, request=request, form=form, change=None)

        c7 = Category(name='Двухдверные холодильники')
        form = CategoryForm(instance=c7)
        form.cleaned_data = {'parent_name': c6.pk}
        self.admin.save_model(obj=c7, request=request, form=form, change=None)

        c8 = Category(name='Смартфоны')
        form = CategoryForm(instance=c8)
        form.cleaned_data = {'parent_name': c3.pk}
        self.admin.save_model(obj=c8, request=request, form=form, change=None)

        categories = (c0, c1, c2, c3, c4, c5, c6, c7, c8, )
        for c in categories:
            c.refresh_from_db()
        return categories
