from django.apps import AppConfig


class ActionLogConfig(AppConfig):
    name = 'actionlog'
    verbose_name = 'Операции склада'

    def ready(self):
        import actionlog.signals
