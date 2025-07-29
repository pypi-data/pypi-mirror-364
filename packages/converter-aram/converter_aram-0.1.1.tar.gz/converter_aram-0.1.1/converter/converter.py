# currency_converter/converter.py

EXCHANGE_RATES = {
    ('USD', 'EUR'): 0.91,
    ('EUR', 'USD'): 1.10,
    ('USD', 'XOF'): 600,
    ('XOF', 'USD'): 0.0017,
    ('EUR', 'XOF'): 655.957,
    ('XOF', 'EUR'): 0.0015
}

def convert(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    key = (from_currency.upper(), to_currency.upper())
    if key in EXCHANGE_RATES:
        return round(amount * EXCHANGE_RATES[key], 2)
    raise ValueError(f"Taux de change non disponible pour {from_currency} -> {to_currency}")
