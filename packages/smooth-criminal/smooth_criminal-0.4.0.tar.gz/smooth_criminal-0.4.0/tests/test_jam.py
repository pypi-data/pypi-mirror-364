from smooth_criminal.core import jam

@jam(workers=3)
def square(x):
    return x * x

def test_jam_parallel_execution():
    inputs = [1, 2, 3, 4, 5]
    expected = [1, 4, 9, 16, 25]
    result = square(inputs)
    assert sorted(result) == expected
