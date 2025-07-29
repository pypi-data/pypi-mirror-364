from converter.converter import convert_currency

def test_convert_currency():
    assert convert_currency(100, 0.85) == 85.0
    assert convert_currency(50, 1.2) == 60.0
    assert convert_currency(0, 10) == 0
