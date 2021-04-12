from typing import Tuple


def ceil_div(a, b):
    return (a + b - 1) // b


def bxor(A: bytes, B: bytes):
    assert isinstance(A, bytes) and isinstance(B, bytes)
    assert len(A) == len(B)

    iA = int.from_bytes(A, "big")
    iB = int.from_bytes(B, "big")
    iR = iA ^ iB
    
    return iR.to_bytes(len(A), "big")
