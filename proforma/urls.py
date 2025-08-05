from django.urls import path
from . import views

app_name = "proforma"

urlpatterns = [
    path("draft/", views.product_selection_view, name="product_selection"),
    path("draft/create/", views.product_selection_view, name="create_draft"),
    path("draft/toggle/<int:product_id>/", views.toggle_product_in_draft, name="toggle_product"),
    path("draft/load-products/", views.load_products_by_category, name="load_products_by_category"),
    path("draft/<int:draft_id>/fill/", views.draft_detail_view, name="fill_draft"),
    path("draft/confirm/", views.confirm_draft_view, name="confirm_draft"),  # Onay ekranı
    path("invoice/<int:invoice_id>/", views.proforma_detail, name="invoice_detail"),
    path("draft/<int:draft_id>/clear/", views.clear_proforma_draft, name="clear_draft"),
    path("invoice/<int:invoice_id>/pdf/", views.generate_proforma_pdf, name="proforma_pdf"),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/<int:pk>/pdf/', views.invoice_pdf_view, name='invoice_pdf')
]
