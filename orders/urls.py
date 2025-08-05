from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('ordercreate/', views.order_create_view, name='ordercreate'),
    path('order/clear/<int:order_id>/', views.clear_order, name='clear_order'),
    path('ajax/update-firma/', views.update_firma_ajax, name='update_firma_ajax'),
    path('ajax/load-products/', views.load_products_by_category, name='load_products_by_category'),
    path('cart/toggle/<int:product_id>/', views.toggle_cart_product, name='toggle_cart_product'),
    path('cart/<int:order_id>/', views.cart_detail, name='cart_detail'),
    path('cart/update/<int:item_id>/', views.cart_update_quantity, name='cart_update_quantity'),
    path('cart/remove/<int:item_id>/', views.cart_remove_item, name='cart_remove_item'),
    path('order/confirm/<int:order_id>/', views.order_confirm, name='order_confirm'),
    path('order/cancel/<int:order_id>/', views.order_cancel, name='order_cancel'),
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/detail/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/preview_pdf/', views.order_preview_pdf, name='order_preview_pdf'),
]
