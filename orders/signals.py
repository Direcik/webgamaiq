from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from notifications.telegram import send_telegram_message
from django.shortcuts import get_object_or_404

@receiver(post_save, sender=Order)
def yeni_siparis_bildirimi(sender, instance, created, **kwargs):
    order = get_object_or_404(Order)
    if created:
        mesaj = (
            f"📦 <b>Yeni Sipariş</b>\n"
            f"🧾 No: {order.order_number}\n"
            f"👤 Müşteri: {order.customer_company.name}\n"
            f"Tarih: {order.order_date}\n"      
        )
        send_telegram_message(mesaj)