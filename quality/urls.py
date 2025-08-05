# quality/urls.py

from django.urls import path
from . import views

app_name = 'quality'

urlpatterns = [
    path('yeni-rapor/', views.create_quality_report, name='create_report'),
    path("raporlar/", views.quality_report_list, name="report_list"),
    path('report/pdf/<int:pk>/', views.quality_report_pdf, name='quality_report_pdf'),
]