from django import forms
from company.models import Company
from inventory.models import Product

class BelgeOlusturForm(forms.Form):
    tarih = forms.DateField(label="Belge Tarihi", widget=forms.DateInput(attrs={'type': 'date'}))
    alici = forms.CharField(label="Kime (Alıcı Kurum)", max_length=200)
    ihale_no = forms.CharField(label="İhale Kayıt No", max_length=100)
    urun = forms.CharField(label="Ürün", max_length=200)
    firma = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        label="Firma Seç",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Ürün (Yalnızca Ürünlü Yetki Belgesi için)",
        required=False
    )