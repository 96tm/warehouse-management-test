from django.core.management.base import BaseCommand
import datetime
import pytz
from warehouse.models import Stock
from category.models import Category
from common.models import SupplierCategory, CargoStock, ShipmentStock
from supplier.models import Supplier
from customer.models import Customer
from shipment.models import Shipment
from cargo.models import Cargo
from django.conf import settings


class Command(BaseCommand):
    help = 'Adds test data to the database'

    def handle(self, *args, **kwargs):
        self.fill_db()
        self.stdout.write(self.style.SUCCESS('OK - data successfully added'))

    def fill_db(self):
        now = datetime.datetime.now(tz=pytz.utc)
        last_week = now - datetime.timedelta(days=7)
        last_month = now - datetime.timedelta(days=31)

        c1 = Category(pk=1, name='Электроника')
        c1.save()
        c2 = Category(pk=2, name='Бытовая техника', parent=c1)
        c2.save()
        c3 = Category(pk=3, name='Телевизоры', parent=c1)
        c3.save()
        c4 = Category(pk=4, name='Телефоны', parent=c1)
        c4.save()
        c5 = Category(pk=5, name='Смартфоны', parent=c4)
        c5.save()
        c6 = Category(pk=6, name='Холодильники', parent=c2)
        c6.save()
        c7 = Category(pk=7, name='Стиральные машины', parent=c2)
        c7.save()
        c8 = Category(pk=8, name='Посудомоечные машины', parent=c2)
        c8.save()
        categories = (c1, c2, c3, c4, c5, c6, c7, c8, )

        stocks = (Stock(pk=1, article=100, category=categories[2],
                        name='Телевизор LG', price=10000,
                        number=10),
                Stock(pk=2, article=101, category=categories[2],
                        name='Телевизор Samsung', price=11000,
                        number=9),
                Stock(pk=3, article=102, category=categories[2],
                        name='Телевизор Sony', price=12000,
                        number=20),
                Stock(pk=4, article=103, category=categories[6],
                        name='Стиральная машина LG', price=10500,
                        number=5),
                Stock(pk=5, article=104, category=categories[4],
                        name='Смартфон Samsung Galaxy Note 8', price=13000,
                        number=18),
                Stock(pk=6, article=105, category=categories[5],
                        name='Холодильник LG', price=10000,
                        number=12),
                Stock(pk=7, article=106, category=categories[5],
                        name='Холодильник Samsung', price=15000,
                        number=0),
                )

        Stock.objects.bulk_create(stocks)

        suppliers = (Supplier(pk=1, organization='LG',
                            address='680000, Хабаровск, ул. Большая, 1-1',
                            phone_number='111111',
                            email='lg_fake@domain.com',
                            legal_details='ИНН: 9909111111',
                            contact_info=('Контактное лицо: '
                                            + 'Сергей Иванович Сидоров')),
                    Supplier(pk=2, organization='Samsung',
                            address='680000, Хабаровск, ул. Большая, 1-2',
                            phone_number='111112',
                            email='samsung_fake@domain.com',
                            legal_details='ИНН: 9909111112',
                            contact_info=('Контактное лицо: '
                                            + 'Сергей Иванович Семенов')),
                    Supplier(pk=3, organization='Sony',
                            address='680000, Хабаровск, ул. Большая, 1-3',
                            phone_number='111113',
                            email='sony_fake@domain.com',
                            legal_details='ИНН: 9909111113',
                            contact_info=('Контактное лицо: '
                                            + 'Сергей Иванович Петров')),
                    )
        Supplier.objects.bulk_create(suppliers)

        for i in range(7):
            sc = SupplierCategory(supplier=suppliers[0],
                                category=categories[i])
            sc.save()
            sc = SupplierCategory(supplier=suppliers[1],
                                category=categories[i])
            sc.save()
        for i in range(6):
            sc = SupplierCategory(supplier=suppliers[2],
                                category=categories[i])
            sc.save()

        customers = (Customer(pk=1, full_name='Иван Иванович Иванов',
                            phone_number='222222',
                            email=settings.CLIENT_EMAIL,
                            contact_info=('Контактное лицо: '
                                            + 'Иван Иванович Иванов')),
                    Customer(pk=2, full_name='Петр Петрович Петров',
                            phone_number='222223',
                            email=settings.CLIENT_EMAIL,
                            contact_info=('Контактное лицо: '
                                            + 'Петр Петрович Петров')),
                    Customer(pk=3, full_name='Светлана Семеновна Семенова',
                            phone_number='222224',
                            email=settings.CLIENT_EMAIL,
                            contact_info=('Контактное лицо: '
                                            + 'Светлана Семеновна Семенова')),
                    Customer(pk=4, full_name='Анна Николаевна Николаева',
                            phone_number='222225',
                            email=settings.CLIENT_EMAIL,
                            contact_info=('Контактное лицо: '
                                            + 'Анна Николаевна Николаева')),

                    )
        Customer.objects.bulk_create(customers)

        cargo = (Cargo(pk=1, supplier=suppliers[0],
                    date=last_week),
                Cargo(pk=2, supplier=suppliers[0],
                    date=last_month),
                Cargo(pk=3, supplier=suppliers[1],
                    date=last_week),
                Cargo(pk=4, supplier=suppliers[1],
                    date=last_week),
                Cargo(pk=5, supplier=suppliers[0],
                    date=last_week),
                )

        Cargo.objects.bulk_create(cargo)

        CargoStock.objects.create(cargo=cargo[0], stock=stocks[0], number=10)
        CargoStock.objects.create(cargo=cargo[1], stock=stocks[3], number=5)
        CargoStock.objects.create(cargo=cargo[1], stock=stocks[5], number=15)
        CargoStock.objects.create(cargo=cargo[2], stock=stocks[0], number=10)
        CargoStock.objects.create(cargo=cargo[2], stock=stocks[4], number=20)
        CargoStock.objects.create(cargo=cargo[3], stock=stocks[6], number=10)
        CargoStock.objects.create(cargo=cargo[4], stock=stocks[6], number=10)

        shipments = (Shipment(pk=1, customer=customers[0],
                            date=now),
                    Shipment(pk=2, customer=customers[0],
                            date=now),
                    Shipment(pk=3, customer=customers[0],
                            date=now),
                    Shipment(pk=4, customer=customers[1],
                            date=now),
                    Shipment(pk=5, customer=customers[2],
                            date=now),
                    Shipment(pk=6, customer=customers[0],
                            date=now),
                    Shipment(pk=7, customer=customers[1],
                            date=now),
                    Shipment(pk=8, customer=customers[2],
                            date=now),
                    )

        Shipment.objects.bulk_create(shipments)

        ShipmentStock.objects.create(shipment=shipments[0],
                                    stock=stocks[6], number=10)
        ShipmentStock.objects.create(shipment=shipments[1],
                                    stock=stocks[4], number=1)
        ShipmentStock.objects.create(shipment=shipments[2],
                                    stock=stocks[5], number=1)
        ShipmentStock.objects.create(shipment=shipments[3],
                                    stock=stocks[5], number=2)
        ShipmentStock.objects.create(shipment=shipments[4],
                                    stock=stocks[0], number=1)
        ShipmentStock.objects.create(shipment=shipments[0],
                                    stock=stocks[4], number=1)
        ShipmentStock.objects.create(shipment=shipments[6],
                                    stock=stocks[5], number=5)
        ShipmentStock.objects.create(shipment=shipments[4],
                                    stock=stocks[5], number=4)
        ShipmentStock.objects.create(shipment=shipments[5],
                                    stock=stocks[4], number=3)
        ShipmentStock.objects.create(shipment=shipments[7],
                                    stock=stocks[2], number=7)
