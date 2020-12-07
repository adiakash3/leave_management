from django.apps import AppConfig


class HolidaysConfig(AppConfig):
    name = 'holidays'
    
    def ready(self):
        import holidays.signals
