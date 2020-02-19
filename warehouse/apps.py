from django.apps import AppConfig


class WarehouseConfig(AppConfig):
    name = 'warehouse'
    verbose_name = 'Склад'

    def ready(self):
        import warehouse.signals
