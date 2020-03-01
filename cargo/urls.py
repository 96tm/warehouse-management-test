from django.urls import path
from . import views

app_name = 'cargo'

urlpatterns = [path('cargo_new',
                    views.CargoFormsetsView.as_view(), name='cargo_new'),
               # path('cargo_new', views.cargo_new, name='cargo_new'),
               path('cargo_list', views.cargo_list, name='cargo_list'),
               path('cargo/<int:pk>/',
                    views.cargo_fill, name='cargo_detail'), ]
