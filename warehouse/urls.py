from django.urls import path

from . import views

app_name = 'warehouse'

urlpatterns = [path('', views.index, name='index'),
               path('order', views.OrderView.as_view(), name='order'),
               path('orderset', views.OrderFormsetsView.as_view(), name='orderset'),
               path('order_successful',
                    views.OrderSuccessfulView.as_view(),
                    name='order_successful'),
               path('cargo_new', views.CargoFormsetsView.as_view(), name='cargo_new'),
               #path('cargo_new', views.cargo_new, name='cargo_new'),
               path('cargo_list', views.cargo_list, name='cargo_list'),
               path('cargo/<int:pk>/', views.cargo_fill, name='cargo_detail'),
               path('shipment_confirmation',
                    views.ShipmentConfirmation.as_view(),
                    name='shipment_confirmation'),
               path('shipment_success', views.shipment_success,
                    name='shipment_success'),
               ]
