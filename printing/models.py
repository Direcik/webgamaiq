from django.db import models
from django.utils import timezone
from django.urls import reverse
import uuid
from inventory.models import Product  # mevcut ürün modelin

class PrintingRef(models.Model):
    ref_no = models.CharField(max_length=50, unique=True, verbose_name="Baskı Ref No")
    kazan_size = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Kazan Ölçüsü (cm)")

    def __str__(self):
        return self.ref_no


class PrintingOrder(models.Model):
    ref = models.ForeignKey(PrintingRef, on_delete=models.PROTECT, verbose_name="Baskı Ref No")
    order_no = models.CharField(max_length=20, unique=True, editable=False)
    paper = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Kullanılacak Kağıt")
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Kg")
    print_surface = models.CharField(
        max_length=10,
        choices=[('ic', 'İç'), ('dis', 'Dış')],
        verbose_name="Baskı Yüzeyi"
    )
    date = models.DateField(default=timezone.now, verbose_name="Tarih")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ref.ref_no} ({self.order_no})"


class PrintingOrderMovement(models.Model):
    MOVEMENT_TYPES = [
        ('raw_out', 'Hammadde Çıkışı'),
        ('semi_in', 'Yarı Mamul Girişi'),
        ('final_in', 'Mamül Girişi'),
    ]

    order = models.ForeignKey(PrintingOrder, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch_no = models.CharField(max_length=50, verbose_name="Parti No")
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.weight_kg} kg)"
