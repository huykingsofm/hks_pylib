import os
import random
from hks_pylib.math import bxor, ceil_div

def simple_xor_bytes(A: bytes, B: bytes):
    assert isinstance(A, bytes) and isinstance(B, bytes)
    assert len(A) == len(B)

    def xor(x):
        return x[0] ^ x[1]

    Z = bytes(map(xor, zip(A, B)))

    return Z


def test_ceil_div():
    a = random.randint(1000, 2000)
    b = random.randint(100, 200)
    c = ceil_div(a, b)
    assert c * b >= a

def run_xor_bytes():
    a = os.urandom(1000000)
    b = os.urandom(1000000)
    return bxor(a, b)

def run_simple_xor_bytes():
    a = os.urandom(1000000)
    b = os.urandom(1000000)
    return simple_xor_bytes(a, b)

def test_benchmark_xor_bytes(benchmark):
    benchmark(run_xor_bytes)
    
def test_benchmark_simple_xor_bytes(benchmark):
    benchmark(run_simple_xor_bytes)

def test_result_bxor():
    a = os.urandom(1000000)
    b = os.urandom(1000000)
    result = bxor(a, b)
    expected = simple_xor_bytes(a, b)
    assert result == expected
