from readtime import estimate_readtime
def test_short_text():
    assert estimate_readtime('dit is een korte tekst.') == 1

def test_longer_text():
    text = 'woord ' * 400
    assert estimate_readtime (text) == 2

