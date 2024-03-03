from django import forms
from .models import Job, Spent
from user.models import Profile

class JobForm(forms.ModelForm):

    client = forms.ModelChoiceField(queryset=Profile.objects.filter(is_client=True), widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'En que consiste el trabajo'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicacion'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Job
        fields = ['client', 'description', 'price', 'image', 'address']
    
    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

class SpentForm(forms.ModelForm):

    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'En que fue el gasto'}))
    amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Spent
        fields = ['description', 'amount', 'image']
    
    def __init__(self, *args, **kwargs):
        super(SpentForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False
