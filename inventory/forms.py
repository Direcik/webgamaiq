from django import forms
from .models import Product, Category, Unit, Warehouse, StockMovement
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from django.core.exceptions import ValidationError
from company.models import Company

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # stock_quantity alanı otomatik yönetildiği için formda yer almaz
        fields = ['ref_no', 'barcode', 'name_tr', 'name_en', 'udino', 'category', 'unit', 'warehouse']
        widgets = {
            'ref_no': forms.TextInput(attrs={'placeholder': 'Referans Numarası'}),
            'barcode': forms.TextInput(attrs={'placeholder': 'Barkod Numarası (isteğe bağlı)'}),
            'name_tr': forms.TextInput(attrs={'placeholder': 'Ürün Adı (Türkçe)'}),
            'name_en': forms.TextInput(attrs={'placeholder': 'Ürün Adı (İngilizce, isteğe bağlı)'}),
            'udino': forms.TextInput(attrs={'placeholder': 'UDI Numarası (isteğe bağlı)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False  # 🔥 Etiketleri gizle
        self.helper.layout = Layout(
            Row(
                Column('ref_no', css_class='form-group col-md-6 mb-2'),
                Column('barcode', css_class='form-group col-md-6 mb-2'),
                css_class='form-row'
            ),
            Row(
                Column('name_tr', css_class='form-group col-md-6 mb-2'),
                Column('name_en', css_class='form-group col-md-6 mb-2'),
                css_class='form-row'
            ),
            'udi_no',
            Row(
                Column('category', css_class='form-group col-md-4 mb-2'),
                Column('unit', css_class='form-group col-md-4 mb-2'),
                Column('warehouse', css_class='form-group col-md-4 mb-2'),
                css_class='form-row'
            ),
            Submit('submit', 'Ürünü Kaydet', css_class='btn btn-primary mt-3')
        )
        # ForeignKey alanlar için boş seçenek ekleyelim
        self.fields['category'].empty_label = "Kategori Seçiniz"
        self.fields['unit'].empty_label = "Birim Seçiniz"
        self.fields['warehouse'].empty_label = "Depo Seçiniz"
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        
class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = '__all__'

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = '__all__'

class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='',  # boş label
        widget=forms.Select(attrs={'placeholder': 'Kategori seçin', 'class': 'form-select'})
    )
    ref_no = forms.CharField(
        required=False,
        label='',  # boş label
        widget=forms.TextInput(attrs={'placeholder': 'Ref No ile ara...', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False  # 🔥 Etiketleri gizle
        self.helper.layout = Layout(
            Row(
                Column('category', css_class='col-md-3 mb-2'),
                Column('ref_no', css_class='col-md-3 mb-2'),
                Column(Submit('submit', 'Filtrele', css_class='btn btn-primary w-100'), css_class='col-md-3 mb-2'),
                Column(
                    HTML('<a href="." class="btn btn-outline-secondary w-100">Temizle</a>'),
                    css_class='col-md-3 mb-2'
                )
            )
        )

# --- Ortak Stok Hareketi Formu (Template) ---

class BaseStockMovementForm(forms.ModelForm):
    # Ürün seçimi yerine barkod alanı
    barcode = forms.CharField(max_length=100,required=True,label="Ürün Barkodu",widget=forms.TextInput(attrs={'placeholder': 'Barkod Numarası', 'id': 'barcode'}))
    product_ref_no = forms.CharField(max_length=50, required=False, label="Referans Numarası", widget=forms.TextInput(attrs={ 'placeholder': 'Referans No', 'id': 'product_ref_no',
            'class': 'form-control'
        })
    )
    # Ürün bilgilerini göstermek için readonly alanlar
    # Bunlar sadece görüntüleme amaçlıdır, form verisi olarak gönderilmez.
    # Ancak yine de form objesinde erişilebilir olması için ekliyoruz.
    product_name_tr = forms.CharField(max_length=255,required=False,label="Ürün Adı",widget=forms.TextInput(attrs={'readonly': 'readonly', 'id': 'product_name_tr'}))
    product_stock_quantity = forms.FloatField(required=False,label="Mevcut Stok",widget=forms.NumberInput(attrs={'readonly': 'readonly', 'id': 'product_stock_quantity'})
)

    # Firma bilgisi (readonly)
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        label="Firma",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = StockMovement
        # product alanı kaldırıldı, barkod üzerinden bulunacak
        fields = ['company', 'quantity', 'lot_no', 'description'] # movement_type view'da ayarlanacak
        widgets = {
            'quantity': forms.NumberInput(attrs={'placeholder': 'Miktar'}),
            'lot_no': forms.TextInput(attrs={'placeholder': 'Lot Numarası (isteğe bağlı)'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Açıklama (isteğe bağlı)'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)  # Firma dışarıdan alınır
        super().__init__(*args, **kwargs)

        # Firma adı ilk değer olarak atanır
        self.fields['company'].initial = company.name if company else 'Firma Seçilmedi'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'company',
            HTML("""
                <div class="mb-3">
                    <label for="product_ref_no" class="form-label">Referans Numarası</label>
                    <input type="text" name="ref_no" class="form-control" id="product_ref_no" placeholder="Referans No">
                    <div id="ref_no_feedback" class="invalid-feedback"></div>
                </div>
            """),
            HTML("""
            <div class="mb-3">
                <label for="barcode" class="form-label">Ürün Barkodu</label>
                <div class="input-group">
                <input type="text" name="barcode" class="form-control" id="barcode" placeholder="Barkod Numarası" required autocomplete="off">
                <button type="button" id="start-camera" class="btn btn-outline-secondary" title="Kamera ile Tara">📷</button>
                </div>
                <div id="barcode_feedback" class="invalid-feedback"></div>
            </div>
            <div id="camera-container" style="display:none; margin-bottom:1rem;">
                <div id="reader" style="width:300px; height:200px;"></div>
                <button type="button" id="close-camera" class="btn btn-danger mt-2">Kapat</button>
            </div>
            """),
            Row(
                Column('product_name_tr', css_class='form-group col-md-8 mb-2'),
                Column('product_stock_quantity', css_class='form-group col-md-4 mb-2'),
                css_class='form-row'
            ),
            'quantity', # Quantity alanı için ekstra JS kontrolü yapacağız
            Row(
                Column('lot_no', css_class='form-group col-md-6 mb-2'),
                Column(Field('description', css_class='form-control'), css_class='form-group col-md-6 mb-2'), # Description'ı satır içine aldık
                css_class='form-row'
            ),
            # Submit butonu, alt sınıflar tarafından eklenecek
        )
        self.fields['quantity'].min_value = 1 # Negatif veya 0 adet girişi engelle
        # Varsayılan olarak product_ref_no ve product_name_tr readonly olmalı
        self.fields['product_ref_no'].widget.attrs['readonly'] = 'readonly'
        self.fields['product_name_tr'].widget.attrs['readonly'] = 'readonly'
        self.fields['product_stock_quantity'].widget.attrs['readonly'] = 'readonly'
        self.fields['company'].widget.attrs['readonly'] = 'readonly'

    def clean_barcode(self):
        barcode = self.cleaned_data['barcode']
        try:
            # Barkodu kullanarak ürünü bulmaya çalış
            product = Product.objects.get(barcode=barcode)
            self.cleaned_data['product'] = product # Ürünü temizlenmiş verilere ekle
        except Product.DoesNotExist:
            raise ValidationError("Bu barkod numarasına sahip bir ürün bulunamadı.")
        return barcode

    # Formun tamamının doğrulanmasından sonra product objesine erişilebilir
    def clean(self):
        cleaned_data = super().clean()
        # Barkod temizleme metodunda ürünü bulduğumuz için burada product'a erişebiliriz
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if not product: # clean_barcode metodundan ürün bulunamadıysa
            raise ValidationError("Ürün barkodu geçerli değil veya bulunamadı.")

        # Bu formun bir stok çıkış formu olup olmadığını kontrol etmek için
        # movement_type'ı instance üzerinden kontrol etmek gerekir.
        # Bu BaseStockMovementForm olduğu için bu kontrolü alt sınıflarda yapalım.

        return cleaned_data
# --- Stok Giriş Formu ---
class StockInForm(BaseStockMovementForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Layout'a submit butonunu ekliyoruz
        self.helper.layout.append(Submit('submit', 'Stok Girişi Kaydet', css_class='btn btn-success mt-3'))
        # Gerekirse StockIn'e özel layout veya alan ekleyebilirsiniz
        # Örneğin, quantity için placeholder'ı güncelleyebilirsiniz.
        self.fields['quantity'].widget.attrs['placeholder'] = 'Giriş Adedi'


# --- Stok Çıkış Formu ---
class StockOutForm(BaseStockMovementForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Layout'a submit butonunu ekliyoruz
        self.helper.layout.append(Submit('submit', 'Stok Çıkışı Kaydet', css_class='btn btn-danger mt-3'))
        # Gerekirse StockOut'a özel layout veya alan ekleyebilirsiniz
        self.fields['quantity'].widget.attrs['placeholder'] = 'Çıkış Adedi'


    # Stok çıkışında ek validasyon
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product') # BaseStockMovementForm'dan geliyor
        quantity = cleaned_data.get('quantity')

        if product and quantity:
            if quantity > product.stock_quantity:
                self.add_error('quantity', f"Yetersiz stok! {product.name_tr} için mevcut stok {product.stock_quantity} adettir.")
        return cleaned_data

    
class StockMovementFilterForm(forms.Form):
    # Yeni: Hareket Tipi seçimi
    MOVEMENT_CHOICES = [
        ('', '-----'), # Boş seçenek (filtreleme yok)
        ('IN', 'Giriş'),
        ('OUT', 'Çıkış'),
    ]
    movement_type = forms.ChoiceField(
        choices=MOVEMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False  # 🔥 Etiketleri gizle
        self.helper.layout = Layout(
            Row(
                Column('movement_type', css_class='col-md-2 mb-2'),
                Column('start_date', css_class='col-md-3 mb-2'),
                Column('end_date', css_class='col-md-3 mb-2'),
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


# Yeni: Kategori Filtreleme Formu
class CategoryFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='',  # boş label
        widget=forms.Select(attrs={'placeholder': 'Kategori seçin', 'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False  # 🔥 Etiketleri gizle
        self.helper.layout = Layout(
            Row(
                Column('category', css_class='col-md-6 mb-2'),
                Column(Submit('submit', 'Filtrele', css_class='btn btn-primary w-100'), css_class='col-md-3 mb-2'),
                Column(
                    HTML('<a href="." class="btn btn-outline-secondary w-100">Temizle</a>'),
                    css_class='col-md-3 mb-2'
                )
            )
        )