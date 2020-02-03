from django.urls import path

from . import views

app_name = 'warehouse'
urlpatterns = [path('', views.index, name='index'),
               path('supplier', views.supplier, name='supplier'),
               path('customer', views.customer, name='customer'),
               path('order_new', views.neworder, name='order_new'),
               path('order_details', views.orderdetails, name='order_details'),
               path('order_list', views.orders_list, name='order_list'), ]
