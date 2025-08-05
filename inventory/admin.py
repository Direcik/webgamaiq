# inventory/admin.py
from django.contrib import admin
from .models import Category, Unit, Warehouse, Product, StockMovement

# Yardımcı Modellerin Admin Paneli Kaydı
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('ref_no', 'barcode', 'name_tr', 'udino', 'category', 'unit', 'warehouse', 'stock_quantity',)
    search_fields = ('ref_no', 'barcode', 'name_tr', 'name_en', 'udino',)
    list_filter = ('category', 'unit', 'warehouse',)
    # stock_quantity alanı otomatik güncellendiği için readonly_fields olarak ayarlanır
    readonly_fields = ('stock_quantity',)

# Stok Hareketleri Admin Paneli Kaydı
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'lot_no', 'user', 'movement_date',)
    list_filter = ('movement_type', 'movement_date', 'user', 'product',)
    search_fields = ('product__name_tr', 'product__ref_no', 'lot_no',)
    # Ürün ve kullanıcı seçimi için raw_id_fields kullanışlıdır
    raw_id_fields = ('product', 'user',)

    # Stok hareketi kaydedilirken otomatik olarak işlem yapan kullanıcıyı al
    def save_model(self, request, obj, form, change):
        if not obj.pk: # Obje yeni oluşturuluyorsa
            obj.user = request.user # Mevcut kullanıcıyı atıyoruz
        super().save_model(request, obj, form, change)