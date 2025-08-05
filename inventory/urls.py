from django.urls import path
from inventory import views

urlpatterns = [
    path('productdashboard/', views.productDashboard, name="productdashboard"),
    path('addproduct/', views.addProduct, name="addproduct"),
    path('updateproduct/<int:id>', views.updateProduct, name="updateproduct"),
    path('deleteproduct/<int:id>', views.deleteProduct, name="deleteproduct"),
    path('addcategory/', views.addCategory, name="addcategory"),
    path('updatecategory/<int:id>', views.updateCategory, name="updatecategory"),
    path('deletecategory/<int:id>', views.deleteCategory, name="deletecategory"),
    path('addunit/', views.addUnit, name="addunit"),
    path('updateunit/<int:id>', views.updateUnit, name="updateunit"),
    path('deleteunit/<int:id>', views.deleteUnit, name="deleteunit"),
    path('addwarehouse/', views.addWarehouse, name="addwarehouse"),
    path('updatewarehouse/<int:id>', views.updateWarehouse, name="updatewarehouse"),
    path('deletewarehouse/<int:id>', views.deleteWarehouse, name="deletewarehouse"),
    path('category/<slug:category_slug>/', views.category_list, name='category_list'),
    path('unit/<slug:unit_slug>/', views.unit_list, name='unit_list'),
    path('warehouse/<slug:warehouse_slug>/', views.warehouse_list, name='warehouse_list'),
    path('item/<slug:product_slug>', views.product_detail, name='product_detail'),
    # Stok Hareketleri Listesi
    path('stock-movements/', views.stock_movement_list, name='stock_movement_list'),

    # Stok Giriş ve Çıkış URL'leri
    path('stock-in/', views.add_stock_in, name='add_stock_in'),
    path('stock-out/', views.add_stock_out, name='add_stock_out'),

    # AJAX için ürün bilgisi URL'i
    path('get-product-by-barcode/', views.get_product_info_by_barcode_json, name='get_product_info_by_barcode_json'),
    path('get-product-info-by-refno-json/', views.get_product_info_by_refno_json, name='get_product_info_by_refno_json'),

    # Ürün Stok Özeti URL'i
    path('stock-summary/', views.product_stock_summary, name='product_stock_summary'),
]
