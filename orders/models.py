# orders/models.py
from django.db import models
from django.conf import settings # Kullanıcı modeline erişmek için
from inventory.models import Product # inventory uygulamanızdaki Product modelini import ediyoruz
from company.models import Company # Eğer şirket/müşteri modeliniz varsa (örneğin Company uygulaması altında)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('confirmed', 'Onaylandı'),
        ('shipped', 'Kargoya Verildi'),
        ('partial', 'Kısmi Teslimat'),
        ('delivered', 'Teslim Edildi'),
        ('invoiced', 'Faturalandı.'),
        ('cancelled', 'İptal Edildi'),
    ]

    # Müşteri veya ilgili şirket (eğer varsa)
    customer_company = models.ForeignKey(
        Company, # Kendi Company modeliniz varsa kullanın, yoksa burayı kaldırın
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orders',
        verbose_name="Müşteri Şirket"
    )
    # Siparişin oluşturulduğu kullanıcı
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_orders',
        verbose_name="Oluşturan Kullanıcı"
    )
    order_number = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="Sipariş Numarası")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Sipariş Tarihi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"
        ordering = ['-order_date']

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE, # Sipariş silindiğinde kalemleri de sil
        related_name='items', # Order objesinden kalemlere erişim için (order.items.all())
        verbose_name="Sipariş"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL, # Ürün silinse bile kalem kalsın ama ürün boş olsun
        null=True, blank=True,
        related_name='order_items',
        verbose_name="Ürün"
    )
    quantity = models.IntegerField(default=1, verbose_name="Miktar")
    delivered_quantity = models.IntegerField(default=0, verbose_name="Teslim Edilen Miktar")
    lot_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lot Numarası")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Sipariş Kalemi"
        verbose_name_plural = "Sipariş Kalemleri"
        # Bir siparişte aynı üründen birden fazla kalem olabilmesi için unique_together kaldırıldı.
        # unique_together = ('order', 'product') # Bir siparişte aynı üründen sadece bir kalem olsun

    def __str__(self):
        return f"{self.quantity} x {self.product.name_tr if self.product else 'Ürün Yok'} ({self.order.order_number})"