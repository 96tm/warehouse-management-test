from django.urls import path
from . import views

app_name = 'cargo'

urlpatterns = [path('cargo_new',
                    views.CargoFormsetsView.as_view(), name='cargo_new'), ]
