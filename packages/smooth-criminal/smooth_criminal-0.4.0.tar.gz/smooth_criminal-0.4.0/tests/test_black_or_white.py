import numpy as np
from smooth_criminal.core import black_or_white

@black_or_white(mode="light")
def double_array(arr):
    return arr * 2

@black_or_white(mode="precise")
def triple_array(arr):
    return arr * 3

def test_black_or_white_light_mode():
    arr = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    result = double_array(arr)
    assert result.dtype == np.float32

def test_black_or_white_precise_mode():
    arr = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    result = triple_array(arr)
    assert result.dtype == np.float64
