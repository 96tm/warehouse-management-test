from django.urls import path

from . import views

app_name = 'shipment'

urlpatterns = [path('shipment_confirmation/<str:qr>/',
                    views.ShipmentConfirmation.as_view(),
                    name='shipment_confirmation'),
               path('order', views.OrderView.as_view(), name='order'),
               path('order_successful',
                    views.OrderSuccessfulView.as_view(),
                    name='order_successful'),
               ]
