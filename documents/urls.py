# documents/urls.py
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path("belge_formu/", views.belge_formu, name="belge_formu"),
]