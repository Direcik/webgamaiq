from django import forms
from inventory.models import Category
from .models import ProformaInvoice

class CategoryFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Kategoriye Göre Filtrele',
        widget=forms.Select(attrs={"class": "form-select"})
    )

class ProformaConfirmForm(forms.ModelForm):
    class Meta:
        model = ProformaInvoice
        fields = ['currency', 'vat_rate', 'exchange_rate']
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'vat_rate': forms.Select(attrs={'class': 'form-select'}),
            'exchange_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'placeholder': 'Örn: 32.8500'
            }),
        }