import os
import random
from hks_pylib.math import bxor, ceil_div, float2int, int2float

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
