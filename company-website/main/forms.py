from django import forms
from .models import Product, Inquiry, Branch

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'quantity_available', 'price', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['product', 'quantity', 'address', 'city', 'phone_number', 'latitude', 'longitude']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g. +1234567890'}),
        }

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'address', 'latitude', 'longitude']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }