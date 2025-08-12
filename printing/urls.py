from django.urls import path
from . import views

app_name = 'printing'

urlpatterns = [
    path('', views.printing_order_list, name='printing_order_list'),
    path('create/', views.printing_order_create, name='printing_order_create'),
    path('<int:pk>/', views.printing_order_detail, name='printing_order_detail'),
]
