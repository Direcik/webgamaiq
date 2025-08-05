from django.db import models
from inventory.models import Product
from decimal import Decimal


CURRENCY_CHOICES = [
        ('TRY', '₺'),
        ('USD', '$'),
        ('EUR', '€'),
    ]


VAT_CHOICES = [
    (Decimal('0.00'), "%0"),
    (Decimal('1.00'), "%1"),
    (Decimal('8.00'), "%8"),
    (Decimal('10.00'), "%10"),
    (Decimal('18.00'), "%18"),
    (Decimal('20.00'), "%20"),
]
class ProformaDraft(models.Model):
    """Sepet gibi davranan geçici proforma yapısı."""
    created_at = models.DateTimeField(auto_now_add=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)  # Firma adı
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, choices=VAT_CHOICES, blank=True, null=True) # KDV (%)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="1 {currency} = ? TRY")

    def __str__(self):
        return f"Taslak #{self.id}"

    def total_items(self):
        return self.items.count()


class ProformaDraftItem(models.Model):
    draft = models.ForeignKey(ProformaDraft, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    added_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="1 {currency} = ? TRY")

    def total_price(self):
        return self.quantity * self.unit_price

    class Meta:
        unique_together = ('draft', 'product')

    def __str__(self):
        return f"{self.product.name_tr}"


class ProformaInvoice(models.Model):
    company_name = models.CharField(max_length=255)
    currency = models.CharField(max_length=3, choices=[
        ('TRY', '₺'),
        ('USD', '$'),
        ('EUR', '€'),
    ])
    created_at = models.DateField(auto_now_add=True)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))  # %
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="1 {currency} = ? TRY")

    def __str__(self):
        return f"Proforma Invoice #{self.pk} - {self.company_name}"

    def get_currency_display(self):
        return dict(self._meta.get_field('currency').choices).get(self.currency, self.currency)

    @property
    def get_total_amount(self):
        return sum(item.total_price() for item in self.items.all())

    @property
    def get_vat_amount(self):
        return self.get_total_amount * (self.vat_rate / Decimal('100'))

    @property
    def get_grand_total(self):
        return self.get_total_amount + self.get_vat_amount
    
    @property
    def get_tl_grand_total(self):
        return (self.get_grand_total) * (self.exchange_rate)


class ProformaItem(models.Model):
    invoice = models.ForeignKey(ProformaInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name_tr} x {self.quantity}"
