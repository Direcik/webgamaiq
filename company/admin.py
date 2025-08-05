from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_number', 'phone', 'email',)
    search_fields = ('name', 'tax_number', 'email',)
    list_filter = ('name',)