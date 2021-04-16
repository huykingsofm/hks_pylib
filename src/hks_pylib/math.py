from hks_pylib.errors import InvalidParameterError


def ceil_div(a, b):
    return (a + b - 1) // b


def bxor(A: bytes, B: bytes):
    if not isinstance(A, bytes) or not isinstance(B, bytes):
        raise InvalidParameterError("Parameter A and B must be bytes objects.")

    if len(A) != len(B):
        raise InvalidParameterError("Parameter A and B must be the same size.")

    iA = int.from_bytes(A, "big")
    iB = int.from_bytes(B, "big")
    iR = iA ^ iB
    
    return iR.to_bytes(len(A), "big")
