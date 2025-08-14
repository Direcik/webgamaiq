from django.db import models
from django.utils import timezone
from inventory.models import Product
import uuid
from inventory.models import StockMovement

class PrintingRef(models.Model):
    ref_no = models.CharField(max_length=50, unique=True, verbose_name="Baskı Ref No")
    kazan_size = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Kazan Ölçüsü (cm)")
    total_semi_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Toplam Yarı Mamul KG")

    def __str__(self):
        return self.ref_no

class PrintingOrder(models.Model):
    ref_no = models.ForeignKey(PrintingRef, on_delete=models.PROTECT, verbose_name="Baskı Ref No")
    order_no = models.CharField(max_length=20, unique=True, editable=False)
    paper = models.ForeignKey(Product, on_delete=models.CASCADE, limit_choices_to={'category__name__iexact': 'KAĞIT'}, verbose_name="Kullanılacak Kağıt")
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam KG")
    surface = models.CharField(max_length=10, choices=[('ic', 'İç'), ('dis', 'Dış')], verbose_name="Baskı Yüzeyi")
    date = models.DateField(default=timezone.now, verbose_name="Tarih")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    @property
    def status(self):
        semi_total = self.movements.filter(movement_type='semi_in').aggregate(total=models.Sum('weight_kg'))['total'] or 0
        if not self.movements.exists():
            return "Oluşturuldu"
        elif semi_total >= self.weight:
            return "Tamamlandı"
        else:
            return "Üretimde"

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
        is_new = self.pk is None  # İlk kayıt mı kontrolü
        super().save(*args, **kwargs)

        if self.movement_type == 'semi_in' and self.semi_ref:
            # Yarı mamul stok güncelleme
            total_semi = self.order.movements.filter(
                movement_type='semi_in',
                semi_ref=self.semi_ref
            ).aggregate(models.Sum('weight_kg'))['weight_kg__sum'] or 0
            self.semi_ref.total_semi_kg = total_semi
            self.semi_ref.save()

        elif self.movement_type == 'final_in' and is_new and self.product:
            # Mamül stoktan düş
            self.product.stock_quantity -= float(self.weight_kg)
            self.product.save()

            # Stok hareketi kaydı
            StockMovement.objects.create(
                product=self.product,
                movement_type='OUT',
                quantity=float(self.weight_kg),
                lot_no=None,
                company=getattr(self.order, 'company', None),
                user=getattr(self.order, 'created_by', None),
                description=f"Baskı siparişi #{self.order.id} için mamul çıkışı"
            )

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
