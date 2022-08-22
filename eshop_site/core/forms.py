from django import forms
from django_countries.fields import CountryField
from django.forms import ModelForm
from .models import Item


PAYMENT_CHOICES = (
    ('B', 'Банковская карта'),
    ('N', 'Наличные')
)


class CheckOutForm(forms.Form):
    street_address = forms.CharField(label='Адрес', widget=forms.TextInput(attrs={'placeholder': 'Ул. Лубянка д.5'}))
    country = CountryField(blank_label='select country').formfield()
    zip = forms.CharField(label='Почтовый индекс')
    payment_option = forms.ChoiceField(label='Способ оплаты', widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CategoryForm(ModelForm):
    class Meta:
        model = Item
        fields = ['category']


