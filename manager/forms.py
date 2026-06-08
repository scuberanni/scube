from django import forms
from .models import Scube_ss, orders, PB_Paid_Entry

class PrForm(forms.ModelForm):
    pr_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    sl_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False) 
    
    class Meta:
        model = Scube_ss
        fields = ['code', 'Catogory', 'name', 'size', 'prize', 'material', 'color', 'pr_date', 'sl_date', 'status', 'image', 'new_pr']
        labels = {
            'code': 'Custom Label for Field 1',
            'Catogory': 'Custom Label for Field 2',
            'name': 'Custom Label for Field 3',
            'size': 'Custom Label for Field 4',
            'prize': 'Custom Label for Field 5',
            'material': 'Custom Label for Field 6',
            'color': 'Custom Label for Field 7',
            'pr_date': 'Custom Label for Field 8',
            'sl_date': 'Custom Label for Field 9',
            'status': 'Custom Label for Field 10',
            'image': 'Custom Label for Field 11',
            'new_pr': 'Custom Label for Field 12',
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = orders
        fields = '__all__'            
           
class ProductPriceEditForm(forms.Form):
    product_ids = forms.ModelMultipleChoiceField(queryset=Scube_ss.objects.all(), widget=forms.CheckboxSelectMultiple)
    new_price = forms.IntegerField()

class PBPaidForm(forms.ModelForm):
    class Meta:
        model = PB_Paid_Entry
        fields = ['date', 'amount', 'description', 'payment_mode']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control border-danger fw-bold form-control-sm'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control border-danger fw-bold text-danger form-control-sm', 'placeholder': 'Amount *'}),
            'description': forms.TextInput(attrs={'class': 'form-control border-danger form-control-sm', 'placeholder': 'Description...'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select border-danger shadow-sm fw-bold form-control-sm'}),
        }