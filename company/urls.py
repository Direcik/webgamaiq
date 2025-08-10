from django.urls import path
from company import views

urlpatterns = [
    path('companydashboard/', views.companyDashboard, name="companydashboard"),
    path('addcompany/', views.addCompany, name="addcompany"),
    path('api/get-company/', views.get_company_from_izibiz, name='get_company_from_izibiz'),
    path('updatecompany/<int:id>', views.updateCompany, name="updatecompany"),
    path('deletecompany/<int:id>', views.deleteCompany, name="deletecompany"),

]