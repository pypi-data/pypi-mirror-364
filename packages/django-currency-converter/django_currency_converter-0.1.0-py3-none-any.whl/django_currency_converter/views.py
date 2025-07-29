from django.shortcuts import render
from .forms import CurrencyForm
from .utils import convert_currency

def currency_view(request):
    result = None
    if request.method == 'POST':
        form = CurrencyForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            from_cur = form.cleaned_data['from_currency']
            to_cur = form.cleaned_data['to_currency']
            result = convert_currency(amount, from_cur, to_cur)
    else:
        form = CurrencyForm()
    return render(request, 'currency_converter/form.html', {'form': form, 'result': result})
