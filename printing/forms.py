from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import PrintingOrder, PrintingOrderMovement, PrintingRef
from inventory.models import Product


class PrintingOrderForm(forms.ModelForm):
    class Meta:
        model = PrintingOrder
        fields = ['ref_no', 'paper', 'surface', 'weight', 'date', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Sadece KAĞIT kategorisindekileri getir
        self.fields['paper'].queryset = Product.objects.filter(category__name__iexact="KAĞIT")
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Kaydet'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Kaydet'))


class PrintingOrderMovementForm(forms.ModelForm):
    class Meta:
        model = PrintingOrderMovement
        fields = ['movement_type', 'product', 'batch_no', 'weight_kg', 'date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Ekle'))

class PrintingRefForm(forms.ModelForm):
    class Meta:
        model = PrintingRef
        fields = ['ref_no', 'kazan_size']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Kaydet'))
