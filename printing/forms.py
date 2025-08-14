from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import PrintingOrder, PrintingOrderMovement, PrintingRef
from inventory.models import Product


class PrintingOrderForm(forms.ModelForm):
    class Meta:
        model = PrintingOrder
        fields = ['ref_no', 'paper', 'weight', 'surface', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paper'].queryset = Product.objects.filter(category__name__iexact='KAĞIT')
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Kaydet'))


class PrintingOrderMovementForm(forms.ModelForm):
    class Meta:
        model = PrintingOrderMovement
        fields = ['product', 'weight_kg']

    def __init__(self, *args, **kwargs):
        movement_type = kwargs.pop('movement_type', None)
        order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Kaydet'))

        if movement_type == 'final_in' and order:
            # Mamul ekleme: product otomatik olarak order.paper olacak
            self.fields['product'].queryset = Product.objects.filter(pk=order.paper.pk)
            self.fields['product'].initial = order.paper
            self.fields['product'].disabled = True  # Değiştirilemez
        elif movement_type == 'semi_in' and order:
            # Yarı mamul ekleme: product alanını gizle, sadece semi_ref üzerinden ref_no kullanılacak
            self.fields['product'].widget = forms.HiddenInput()
            self.fields['product'].required = False
            # Semi_ref bilgisi formdan gönderilmeyecek, views.py'de order.ref_no atanacak


class PrintingRefForm(forms.ModelForm):
    class Meta:
        model = PrintingRef
        fields = ['ref_no', 'kazan_size', 'total_semi_kg']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Kaydet'))


class PrintingOrderFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
