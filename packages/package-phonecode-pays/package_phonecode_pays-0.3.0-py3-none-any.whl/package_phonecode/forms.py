from django import forms

class CountryForm(forms.Form):
    country = forms.CharField(label="Entrez un pays", max_length=100)
