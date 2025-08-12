"""
URL configuration for WEBgamaIQ project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from orders import views
from printing import views
from quality import views
from proforma import views
from documents import views
from inventory import views
from company import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('user/', include("user.urls")),
    path('user/', include('django.contrib.auth.urls')),
    path('inventory/', include("inventory.urls")),
    path('company/', include("company.urls")),
    path('orders/', include('orders.urls')),
    path('proforma/', include('proforma.urls')),
    path('documents/', include('documents.urls')),
    path('quality/', include('quality.urls')),
    path('printing/', include('printing.urls')),
]