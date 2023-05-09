from django.apps import AppConfig


class PayoutConfig(AppConfig):
    name = 'payouts'

    def ready(self):
        import payouts.signals
