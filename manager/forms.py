
from django.forms import ModelForm
from . models import Scube_ss,orders

class PrForm(ModelForm):
      class Meta:
            model=Scube_ss
            fields='__all__'

class OrderForm(ModelForm):
      class Meta:
            model=orders
            fields='__all__'            
           
from django import forms
from .models import Scube_ss

class ProductPriceEditForm(forms.Form):
    product_ids = forms.ModelMultipleChoiceField(queryset=Scube_ss.objects.all(), widget=forms.CheckboxSelectMultiple)
    new_price = forms.IntegerField()
           

