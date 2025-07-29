from django.apps import AppConfig


class UseappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'useapp'

def ready(self):
    import notifications.signals

