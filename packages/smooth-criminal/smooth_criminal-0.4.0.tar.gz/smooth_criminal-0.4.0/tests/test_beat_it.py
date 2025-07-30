from smooth_criminal.core import beat_it

def fallback_add(x):
    return x + 1

@beat_it(fallback_func=fallback_add)
def faulty_add(x):
    return x + "💥"  # Provocará TypeError

def test_beat_it_fallback():
    result = faulty_add(10)
    assert result == 11
