from django.conf import settings
from django.db import models
from autoslug.fields import AutoSlugField
from django.urls import reverse
from django.core.validators import RegexValidator
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Kategori Adı")
    slug = AutoSlugField(populate_from='name', unique=True, verbose_name='Link Oluşturucu', unique_for_date='publish')
    class Meta:
        verbose_name_plural = 'Kategoriler'
        
    def get_absolute_url(self):
        return reverse('category_list', args=[self.slug])

    def __str__(self):
        return self.name
    
class Unit(models.Model):
    name = models.CharField(max_length=50, verbose_name="Birim")
    slug = AutoSlugField(populate_from='name', unique=True, verbose_name='Link Oluşturucu', unique_for_date='publish')
    class Meta:
        verbose_name_plural = 'Birimler'
        
    def get_absolute_url(self):
        return reverse('unit_list', args=[self.slug])

    def __str__(self):
        return self.name
    
class Warehouse(models.Model):
    name = models.CharField(max_length=50, verbose_name="Depo")
    slug = AutoSlugField(populate_from='name', unique=True, verbose_name='Link Oluşturucu', unique_for_date='publish')
    class Meta:
        verbose_name_plural = 'Depolar'
        
    def get_absolute_url(self):
        return reverse('warehouse_list', args=[self.slug])

    def __str__(self):
        return self.name

    
class Product(models.Model):
    ref_no = models.CharField(max_length = 15, verbose_name='REF NO', blank=True)
    barcode = models.CharField(max_length = 13, verbose_name="Barkod Numarası", validators=[RegexValidator(regex='^\d+$', message='Sadece rakam giriniz')], blank=True)
    name_tr = models.CharField(max_length = 255, verbose_name='Ürün Adı TR', blank=True)
    name_en = models.CharField(max_length = 255, verbose_name='Ürün Adı EN', blank=True)
    udino = models.CharField(max_length = 20 ,verbose_name="UDI Numarası", blank=True)
    stock_quantity = models.FloatField(default=0, verbose_name="Mevcut Stok Adedi")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Kategori Adı')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Birim')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Depo')

    slug = AutoSlugField(populate_from='ref_no', unique=True, verbose_name='Link Oluşturucu', unique_for_date='publish')
    
    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = 'Ürünler'
        ordering = ['ref_no']
    
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])    

    def __str__(self) -> str:
        return self.ref_no
    

class StockMovement(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='stock_movements',verbose_name="Ürün")
    movement_type_choices = [
        ('IN', 'Giriş'),
        ('OUT', 'Çıkış'),
    ]
    movement_type = models.CharField(max_length=3,choices=movement_type_choices,verbose_name="Hareket Tipi")
    quantity = models.FloatField(verbose_name="Miktar")
    lot_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lot Numarası")
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, null=True, blank=True)

    # İşlemi yapan kullanıcı bilgisi
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="İşlem Yapan Kullanıcı")
    # Hareketin otomatik oluşturulduğu tarih
    movement_date = models.DateTimeField(default=timezone.now, verbose_name="Hareket Tarihi")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Stok Hareketi"
        verbose_name_plural = "Stok Hareketleri"
        ordering = ['-movement_date']

    def __str__(self):
        return f"{self.product.name_tr} - {self.get_movement_type_display()} {self.quantity} Adet ({self.movement_date.strftime('%Y-%m-%d %H:%M')})"