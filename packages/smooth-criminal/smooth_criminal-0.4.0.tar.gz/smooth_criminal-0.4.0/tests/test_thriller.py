from smooth_criminal.core import thriller

@thriller
def simple_loop():
    total = 0
    for i in range(1000):
        total += i
    return total

def test_thriller_runs():
    result = simple_loop()
    assert result == sum(range(1000))
