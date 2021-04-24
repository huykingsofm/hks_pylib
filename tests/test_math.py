import os
import random
from hks_pylib.math import Bitwise, bxor, ceil_div, float2int, int2float

def test_ceil_div():
    a = random.randint(1000, 2000)
    b = random.randint(100, 200)
    c = ceil_div(a, b)
    assert c * b >= a


def run_xor_bytes():
    a = os.urandom(1000000)
    b = os.urandom(1000000)
    return bxor(a, b)


def test_benchmark_xor_bytes(benchmark):
    benchmark(run_xor_bytes)


def test_bitwise():
    assert Bitwise.max_natural_number(8) == 255
    assert Bitwise.turn_on_bits(10, 0, 1) == 11
    assert Bitwise.turn_off_bits(11, 0, 1) == 10
    assert Bitwise.get_bits(10, 1, 2) == 2
    assert Bitwise.set_bits(10, 1, 3) == 11