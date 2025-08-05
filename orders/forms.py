# orders/forms.py
from django import forms
from .models import Order, OrderItem # orders uygulamamızdaki modelleri import ettik
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML


ORDER_STATUS_CHOICES = [
        ('', '------'),  # Boş değer
        ('confirmed', 'Onaylandı'),
        ('shipped', 'Kargoya Verildi'),
        ('partial', 'Kısmi Teslimat'),
        ('delivered', 'Teslim Edildi'),
        ('invoiced', 'Faturalandı.'),
        ('cancelled', 'İptal Edildi'),
]



class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'lot_no', 'description']
        widgets = {
            'product': forms.HiddenInput(), # Bu, arka planda ürün ID'sini tutacak gizli alan
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'lot_no': forms.TextInput(attrs={'placeholder': 'Lot Numarası (isteğe bağlı)', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Kalem Açıklaması (isteğe bağlı)', 'class': 'form-control'}),
        }


class OrderCompanyForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_company']
        widgets = {
            'customer_company': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_company'].required = True
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False
        # form_action isteğe göre ayarlanabilir
        # self.helper.form_action = reverse_lazy('complete_order', kwargs={'order_id': self.instance.id})  # örnek
        self.helper.layout = Layout(
            'customer_company',
            # butonları istersen buraya ekleyebilirsin (ama JS kontrolü için template'te kalması mantıklı olabilir)
        )

class OrderItemUpdateForm(forms.ModelForm):
    new_delivery = forms.IntegerField(
        required=False,
        label='Yeni Teslimat',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yeni Teslimat'
        })
    )

    lot_no = forms.CharField(
        required=False,
        label='Lot No',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Lot No'
        })
    )

    class Meta:
        model = OrderItem
        fields = []  # Model alanı yok, sadece custom alanlar var


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class OrderFilterForm(forms.Form):
    order_number = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Sipariş No', 'class': 'form-control'
    }))
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date', 'class': 'form-control'
    }))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date', 'class': 'form-control'
    }))
    status = forms.ChoiceField(choices=ORDER_STATUS_CHOICES, required=False, widget=forms.Select(attrs={
        'class': 'form-select'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column('order_number', css_class='col-md-2 mb-2'),
                Column('start_date', css_class='col-md-2 mb-2'),
                Column('end_date', css_class='col-md-2 mb-2'),
                Column('status', css_class='col-md-2 mb-2'),
                Column(Submit('submit', 'Filtrele', css_class='btn btn-primary w-100'), css_class='col-md-2 mb-2'),
                Column(
                    HTML('<a href="." class="btn btn-outline-secondary w-100">Temizle</a>'),
                    css_class='col-md-2 mb-2'
                )
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Başlangıç tarihi bitiş tarihinden sonra olamaz.")
        return cleaned_data
