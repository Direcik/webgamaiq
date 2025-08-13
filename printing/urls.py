from django.urls import path
from . import views

app_name = 'printing'

urlpatterns = [
    path('', views.printing_order_list, name='printing_order_list'),
    path('create/', views.printing_order_create, name='printing_order_create'),
    path('<int:pk>/', views.printing_order_detail, name='printing_order_detail'),
    path('<int:pk>/add_movement/<str:movement_type>/', views.add_movement, name='add_movement'),
    path('ref/list/', views.printing_ref_list, name='printing_ref_list'),
    path('ref/add/', views.printing_ref_add, name='printing_ref_add'),
    path('ref/<int:pk>/edit/', views.printing_ref_edit, name='printing_ref_edit'),
    path('ref/<int:pk>/delete/', views.printing_ref_delete, name='printing_ref_delete'),
]
