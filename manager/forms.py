
from django.forms import ModelForm
from . models import Scube_ss,orders
from django import forms


class PrForm(ModelForm):
      pr_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
      sl_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False) 
      class Meta:
            model=Scube_ss
            fields=['code','Catogory', 'name', 'size','prize', 'material', 'color','pr_date','sl_date','status','image']
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
        }

class OrderForm(ModelForm):
      class Meta:
            model=orders
            fields='__all__'            
           
from django import forms
from .models import Scube_ss

class ProductPriceEditForm(forms.Form):
    product_ids = forms.ModelMultipleChoiceField(queryset=Scube_ss.objects.all(), widget=forms.CheckboxSelectMultiple)
    new_price = forms.IntegerField()
           

