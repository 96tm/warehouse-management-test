from django.urls import path

from . import views

app_name = 'warehouse'
urlpatterns = [path('', views.index, name='index'),
               path('supplier', views.supplier, name='supplier'),
               path('customer', views.OrderView.as_view(), name='order'),
               path('order_successful', views.OrderSuccessfulView.as_view(), name='order_successful'),
               ]