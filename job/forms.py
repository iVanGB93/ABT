from django import forms
from .models import Job, Spent

class JobForm(forms.ModelForm):

    client = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'En que consiste el trabajo'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicacion'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Job
        fields = ['client', 'description', 'price', 'image', 'address']

class SpentForm(forms.ModelForm):

    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'En que fue el gasto'}))
    amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Spent
        fields = ['description', 'amount', 'image']
