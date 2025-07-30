from django import forms

class CurrencyForm(forms.Form):
    amount = forms.FloatField(label="Montant")
    from_currency = forms.CharField(label="Devise source", max_length=3)
    to_currency = forms.CharField(label="Devise cible", max_length=3)
