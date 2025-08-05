from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory' # Uygulama adınız

    def ready(self):
        import inventory.signals # Sinyalleri yüklüyoruz