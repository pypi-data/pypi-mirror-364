from django.shortcuts import render
from .forms import CurrencyForm

# Exemple de taux statiques (à remplacer avec une API réelle)
CONVERSION_RATES = {
    ('USD', 'EUR'): 0.85,
    ('EUR', 'USD'): 1.18,
    ('XOF', 'EUR'): 0.0015,
    ('EUR', 'XOF'): 655.957,
}

def convert_currency(request):
    result = None
    if request.method == "POST":
        form = CurrencyForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            from_currency = form.cleaned_data['from_currency'].upper()
            to_currency = form.cleaned_data['to_currency'].upper()
            rate = CONVERSION_RATES.get((from_currency, to_currency), None)
            if rate:
                result = amount * rate
            else:
                result = "Conversion non disponible"
    else:
        form = CurrencyForm()
    return render(request, 'monnaie_converter/converter.html', {'form': form, 'result': result})
