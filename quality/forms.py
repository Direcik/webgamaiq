from django import forms
from .models import QualityReport
from inventory.models import Product, Category
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML


class DisabledPlaceholderSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value == '':
            option['attrs']['disabled'] = True
            option['attrs']['hidden'] = True
        return option


class CategoryFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Kategori Seçiniz",
        label='',
        widget=DisabledPlaceholderSelect(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False
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


class QualityReportForm(forms.ModelForm):
    class Meta:
        model = QualityReport
        exclude = ['report_number', 'created_at']

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('selected_category', None)
        super().__init__(*args, **kwargs)

        # İngilizce karşılıklar için sözlükler
        self.paper_translations = {
            "Medikal Kraft Kağıt": "Medical Kraft Paper",
            "Tyvek": "Tyvek"
        }
        self.film_translations = {
            "CPP+PET": "CPP+PET",
            "PET+PE": "PET+PE"
        }

        if category:
            self.fields['product'].queryset = Product.objects.filter(category=category)
        else:
            self.fields['product'].queryset = Product.objects.none()

        for field in self.fields.values():
            field.label = False

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('product', css_class='form-group col-md-6 mb-3'),
                Column('lot_number', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('production_date', css_class='form-group col-md-3 mb-3'),
                Column('expiry_date', css_class='form-group col-md-3 mb-3'),
                Column('paper', css_class='form-group col-md-3 mb-3'),
                Column('film', css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column('paper_weight', css_class='form-group col-md-3 mb-3'),
                Column('film_weight', css_class='form-group col-md-3 mb-3'),
                Column('paper_thickness', css_class='form-group col-md-3 mb-3'),
                Column('film_thickness', css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column('seal_strength_left', css_class='form-group col-md-4 mb-3'),
                Column('seal_strength_right', css_class='form-group col-md-4 mb-3'),
                Column('seal_strength_top', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('size_check', css_class='form-group col-md-4 mb-3'),
                Column('leakage_test', css_class='form-group col-md-4 mb-3'),
                Column('peeling_direction', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('indicator_1', css_class='form-group col-md-3 mb-3'),
                Column('indicator_1_color_change', css_class='form-group col-md-3 mb-3'),
                Column('indicator_2', css_class='form-group col-md-3 mb-3'),
                Column('indicator_2_color_change', css_class='form-group col-md-3 mb-3'),
            ),
            Submit('submit', 'Kaydet', css_class='btn btn-success w-100 mt-3')
        )

        self.fields['production_date'] = forms.DateField(
            label='',
            help_text='Üretim Tarihi Seçiniz',
            widget=forms.DateInput(attrs={
                'type': 'month',
                'class': 'form-control'
            }),
            input_formats=['%Y-%m'],
            required=False
        )

        self.fields['expiry_date'] = forms.DateField(
            label='',
            help_text='Üretim tarihine göre otomatik hesaplanır.',
            widget=forms.DateInput(
                attrs={
                    'type': 'month',
                    'class': 'form-control',
                    'readonly': 'readonly'
                }
            ),
            input_formats=['%Y-%m'],
            required=False
        )

        placeholders = {
            'lot_number': 'Lot No',
            'paper_weight': 'Kağıt Ağırlığı (g/m²)',
            'film_weight': 'Film Ağırlığı (g/m²)',
            'paper_thickness': 'Kağıt Kalınlığı (μm)',
            'film_thickness': 'Film Kalınlığı (μm)',
            'seal_strength_left': 'Kaynak Direnci Sol (N)',
            'seal_strength_right': 'Kaynak Direnci Sağ (N)',
            'seal_strength_top': 'Kaynak Direnci Üst (N)',
            'indicator_1_color_change': 'İndikatör Renk Dönüşümü',
            'indicator_2_color_change': 'İndikatör Renk Dönüşümü',
        }
        for field_name, placeholder in placeholders.items():
            self.fields[field_name].widget.attrs.update({'placeholder': placeholder})

        def set_select_placeholder(field_name, placeholder):
            self.fields[field_name].widget = DisabledPlaceholderSelect()
            self.fields[field_name].choices = [('', placeholder)] + list(self.fields[field_name].choices)

        set_select_placeholder('product', 'Ürün Seçiniz')
        set_select_placeholder('paper', 'Kağıt Seçiniz')
        set_select_placeholder('film', 'Film Seçiniz')
        set_select_placeholder('size_check', 'Boyut Kontrolü ?')
        set_select_placeholder('leakage_test', 'Sızıntı Testi ?')
        set_select_placeholder('peeling_direction', 'Sıyrılma Yönü ?')
        set_select_placeholder('indicator_1', 'İndikatör Seçiniz')
        set_select_placeholder('indicator_2', 'İndikatör Seçiniz')


class QualityReportSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Ürün Adı veya LOT NO ile ara', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column('q', css_class='col-md-6 mb-2'),
                Column(Submit('submit', 'Filtrele', css_class='btn btn-primary w-100'), css_class='col-md-3 mb-2'),
                Column(
                    HTML('<a href="." class="btn btn-outline-secondary w-100">Temizle</a>'),
                    css_class='col-md-3 mb-2'
                )
            )
        )
