from currency_converter.converter import convert

def test_usd_to_eur():
    assert convert(100, 'USD', 'EUR') == 91.0

def test_same_currency():
    assert convert(50, 'EUR', 'EUR') == 50
