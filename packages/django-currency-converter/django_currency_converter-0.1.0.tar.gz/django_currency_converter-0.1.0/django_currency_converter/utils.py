def convert_currency(amount, from_currency, to_currency):
    # Taux de change fictifs
    rates = {
        'USD': 1.0,
        'EUR': 0.9,
        'XOF': 600.0,
        'GBP': 0.8,
    }
    if from_currency not in rates or to_currency not in rates:
        raise ValueError("Devise non supportée")

    usd_amount = amount / rates[from_currency]
    return usd_amount * rates[to_currency]
