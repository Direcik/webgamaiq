from django.db import models
from django.utils import timezone
from inventory.models import Product
from django.db.models import Sum
from django.urls import reverse
from io import BytesIO
import base64
import qrcode
import uuid


class PrintingRef(models.Model):
    ref_no = models.CharField(max_length=50, unique=True, verbose_name="Baskı Ref No")
    kazan_size = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Kazan Ölçüsü (cm)")
    total_semi_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Toplam Yarı Mamul KG")

    def __str__(self):
        return self.ref_no

class PrintingOrder(models.Model):
    ref_no = models.ForeignKey('PrintingRef', on_delete=models.PROTECT, verbose_name="Baskı Ref No")
    order_no = models.CharField(max_length=20, unique=True, editable=False)
    paper = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        limit_choices_to={'category__name__iexact': 'KAĞIT'}, 
        verbose_name="Kullanılacak Kağıt"
    )
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam KG")
    surface = models.CharField(max_length=10, choices=[('ic', 'İç'), ('dis', 'Dış')], verbose_name="Baskı Yüzeyi")
    date = models.DateField(default=timezone.now, verbose_name="Tarih")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    
    # Manuel tamamlandı durumu için alan
    status_override = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    @property
    def status(self):
        # Eğer manuel tamamlandı işaretlenmişse onu döndür
        if self.status_override:
            return self.status_override

        semi_total = self.movements.filter(movement_type='semi_in').aggregate(total=models.Sum('weight_kg'))['total'] or 0
        if not self.movements.exists():
            return "Oluşturuldu"
        elif semi_total >= self.weight:
            return "Tamamlandı"
        else:
            return "Üretimde"

    def get_absolute_url(self):
        return reverse('printing:printing_order_detail', args=[self.pk])

    def generate_qr_code_base64(self, url):
        """Verilen URL için QR kod oluşturur ve base64 string olarak döndürür"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    def __str__(self):
        return f"{self.ref_no.ref_no} ({self.order_no})"

class PrintingOrderMovement(models.Model):
    MOVEMENT_TYPES = [
        ('final_in', 'Mamül Girişi'),
        ('semi_in', 'Yarı Mamul Girişi'),
    ]

    order = models.ForeignKey(PrintingOrder, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)  # Mamul için
    semi_ref = models.ForeignKey(PrintingRef, on_delete=models.CASCADE, null=True, blank=True)  # Yarı mamul için
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Yarı mamul ekleme durumunda PrintingRef.total_semi_kg güncelle
        if self.movement_type == 'semi_in' and self.semi_ref:
            total_semi = self.order.movements.filter(movement_type='semi_in', semi_ref=self.semi_ref).aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0
            self.semi_ref.total_semi_kg = total_semi
            self.semi_ref.save()

    def __str__(self):
        if self.movement_type == 'final_in':
            return f"{self.get_movement_type_display()} - {self.product.name} ({self.weight_kg} kg)"
        else:
            return f"{self.get_movement_type_display()} - {self.semi_ref.ref_no} ({self.weight_kg} kg)"
        

class SemiFinishedStock(models.Model):
    order = models.ForeignKey(PrintingOrder, on_delete=models.CASCADE, related_name='semi_stock')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.product.name} - {self.weight_kg} kg ({self.order.order_no})"
