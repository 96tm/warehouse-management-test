from django.urls import path

from . import views

app_name = 'warehouse'
urlpatterns = [path('', views.index, name='index'),
               path('supplier', views.supplier, name='supplier'),
               path('customer', views.order, name='order'), ]