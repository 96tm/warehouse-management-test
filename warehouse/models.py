from django.core.validators import MinValueValidator
from django.db import models
import uuid
# Create your models here.
from django.db.models import ManyToManyField


class Category(models.Model):
    name = models.CharField(max_length=80)
    parent_id = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    organization = models.CharField(max_length=80)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    legal_details = models.TextField()
    contact_info = models.TextField(null=True)
    categories = models.ManyToManyField(Category, through='SupplierCategory')
    objects = models.Manager()

    def __str__(self):
        return self.organization


class Customer(models.Model):
    full_name = models.CharField(max_length=80)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    contact_info = models.TextField(null=True)

    def __str__(self):
        return self.full_name


class Stock(models.Model):
    article = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    price = models.FloatField()
    number = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Shipment(models.Model):
    DONE = 'Исполнено'
    CREATED = 'Проверка'
    SENT = 'Собрано'
    CANCELLED = 'Отменено'
    choices = [(DONE, DONE), (CREATED, CREATED),
               (SENT, SENT), (CANCELLED, CANCELLED), ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=9, choices=choices)
    date = models.DateTimeField(auto_now_add=True)
    qr = models.TextField(null=True)
    stocks = models.ManyToManyField(Stock, through='ShipmentStock')

    def __str__(self):
        return str(self.customer) + ', ' + self.status + ', ' + str(self.date)


# class Cargo(models.Model):
#     DONE = 'Исполнено'
#     IN_TRANSIT = 'В пути'
#     choices = [(DONE, DONE), (IN_TRANSIT, IN_TRANSIT)]
#
#     supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
#     status = models.CharField(max_length=9, choices=choices, default=IN_TRANSIT)
#     date = models.DateTimeField(auto_now_add=True)
#     stocks = models.ManyToManyField(Stock, through='CargoStock')
#
#     def __str__(self):
#         return str(self.supplier) + ', ' + self.status + ', ' + str(self.date)

class Cargo(models.Model):
    DONE = 'Исполнено'
    IN_TRANSIT = 'В пути'
    choices = [(DONE, DONE), (IN_TRANSIT, IN_TRANSIT)]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    status = models.CharField(max_length=9, choices=choices, default=IN_TRANSIT)
    date = models.DateTimeField(auto_now_add=True)
    stocks = models.ManyToManyField(Stock, through='CargoStock')

    def __str__(self):

        return str(self.pk) + ', ' + str(self.supplier) + ', ' + self.status + ', ' + str(self.date)


class CargoDetails(models.Model):
    order_number = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    quantity = models.SmallIntegerField(default=1)

    def __str__(self):
        return str(self.order_number.pk) + ', ' + str(self.name) + ', ' + str(self.quantity)


class ShipmentStock(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True)
    stock = models.ForeignKey(Stock,
                                 on_delete=models.SET_NULL,
                                 null=True)
    number = models.IntegerField()

    class Meta:
        unique_together = (("shipment", "stock"),)


class CargoStock(models.Model):
    cargo = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True)
    number = models.IntegerField()

    class Meta:
        unique_together = (("cargo", "stock"),)


class SupplierCategory(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = (("supplier", "category"),)
