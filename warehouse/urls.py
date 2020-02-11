from django.urls import path

from . import views

app_name = 'warehouse'

urlpatterns = [path('', views.index, name='index'),
               path('supplier', views.supplier, name='supplier'),
               path('customer', views.customer, name='customer'),
               path('cargo_new', views.cargo_new, name='cargo_new'),
               path('cargo_list', views.cargo_list, name='cargo_list'),
               path('cargo/<int:pk>/', views.cargo_fill, name='cargo_detail'), ]
               path('shipment_confirmation',
                    views.ShipmentConfirmation.as_view(),
                    name='shipment_confirmation'),
               path('shipment_success', views.shipment_success,
                    name='shipment_success')
               ]
