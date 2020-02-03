from django.contrib import admin
from .models import Supplier, Customer, Stock, Category, Cargo, CargoDetails

# Register your models here.

admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Stock)
admin.site.register(Category)
admin.site.register(Cargo)
admin.site.register(CargoDetails)
