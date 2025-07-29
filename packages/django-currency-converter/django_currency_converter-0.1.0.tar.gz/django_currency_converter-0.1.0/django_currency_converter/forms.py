from django import forms

CURRENCY_CHOICES = [
    ('USD', 'Dollar'),
    ('EUR', 'Euro'),
    ('XOF', 'Franc CFA'),
    ('GBP', 'Livre sterling'),
]

class CurrencyForm(forms.Form):
    amount = forms.DecimalField(label="Montant", min_value=0)
    from_currency = forms.ChoiceField(label="De", choices=CURRENCY_CHOICES)
    to_currency = forms.ChoiceField(label="À", choices=CURRENCY_CHOICES)
