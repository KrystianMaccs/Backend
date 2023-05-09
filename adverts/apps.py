from django.apps import AppConfig


class AdvertsConfig(AppConfig):
    name = 'adverts'

    def ready(self):
        import adverts.signals
