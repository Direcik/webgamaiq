from django.contrib import admin
from django.urls import path, include

from orders import views as orders_views
from quality import views as quality_views
from proforma import views as proforma_views
from documents import views as documents_views
from inventory import views as inventory_views
from company import views as company_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ana sayfa için örneğin orders uygulamasının index fonksiyonunu kullanıyoruz
    path('', orders_views.index, name="index"),

    path('user/', include("user.urls")),
    path('user/', include('django.contrib.auth.urls')),
    path('inventory/', include("inventory.urls")),
    path('company/', include("company.urls")),
    path('orders/', include('orders.urls')),
    path('proforma/', include('proforma.urls')),
    path('documents/', include('documents.urls')),
    path('quality/', include('quality.urls')),
]
