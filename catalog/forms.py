from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'quantity',
            'unit_of_measurement',
            'photo',
            'ingredients',
            'is_active',
            'category',
            'manufacturer'
        ]
