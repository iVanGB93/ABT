from django import forms
from .models import Item_List


class ItemForm(forms.ModelForm):

    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'name...'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'description...'}))
    amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 1}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Item_List
        fields = ['name', 'description', 'amount', 'price', 'image']
    
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['description'].required = False

