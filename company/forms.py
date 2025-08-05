from django import forms
from .models import Company
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"
        

class CompanyFilterForm(forms.Form):
    name = forms.CharField(
        required=False,
        label='',  # boş label
        widget=forms.TextInput(attrs={'placeholder': 'Firma Adı', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False  # 🔥 Etiketleri gizle
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6 mb-0'),
                Column(Submit('submit', 'Filtrele', css_class='btn btn-primary w-100'), css_class='col-md-3 mb-2'),
                Column(
                    HTML('<a href="." class="btn btn-outline-secondary w-100">Temizle</a>'),
                    css_class='col-md-3 mb-2'
                )
            )
        )