from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import StockMovement

@receiver(post_save, sender=StockMovement)
def update_product_stock_on_save(sender, instance, created, **kwargs):
    product = instance.product
    if created: # Sadece yeni bir hareket oluşturulduğunda
        if instance.movement_type == 'IN':
            product.stock_quantity += instance.quantity
        elif instance.movement_type == 'OUT':
            product.stock_quantity -= instance.quantity
    # Not: Mevcut bir StockMovement güncellendiğinde, stok miktarını doğru yönetmek
    # daha karmaşık bir mantık gerektirebilir (eski değeri kontrol etme vb.).
    # Bu örnek, yeni oluşturulan hareketleri hedefliyor.
    product.save()

@receiver(post_delete, sender=StockMovement)
def revert_product_stock_on_delete(sender, instance, **kwargs):
    product = instance.product
    if instance.movement_type == 'IN':
        product.stock_quantity -= instance.quantity # Giriş silinirse stoktan düş
    elif instance.movement_type == 'OUT':
        product.stock_quantity += instance.quantity # Çıkış silinirse stoka ekle
    product.save()