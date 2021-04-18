from hks_pylib.cryptography.batchcrypt.batchnumber import GenericBatchNumber
from hks_pylib.cryptography.batchcrypt.batchnumber import BatchNumber, SignedBatchNumber

from hks_pylib.errors.cryptography.batchcrypt.integer import *
from hks_pylib.errors.cryptography.batchcrypt.batchnumber import *


def test_batchnumber():
    print("\nBatchNumber")
    a = BatchNumber.bind(2, 3, 4, bit_length=8)
    b = BatchNumber.bind(2, 4, 6, bit_length=8)

    assert a.get(0) == 2
    assert a.get(1) == 3
    assert a.get(2) == 4

    try:
        a.get(3)
        assert False
    except InvalidElementBatchNumberError:
        pass

    assert b[0] == 2
    assert b[1] == 4
    assert b[2] == 6

    c = a + b
    assert c.get(0) == 4
    assert c.get(1) == 7
    assert c.get(2) == 10


def test_generic_batchnumber():
    A = [0.3, 2.7, 4.6, -3.2, 1.2, -7.4]
    B = [4.5, -2.0, 3.1, 1.24, 3.3, 5.8]

    quantizer = GenericBatchNumber.quantizer()
    quantizer.set_float_range(-20.0, 20.0)
    quantizer.set_int_size(32)
    quantizer.compile()

    batchA = GenericBatchNumber.bind(*A, bit_length=32)
    batchB = GenericBatchNumber.bind(*B, bit_length=32)

    batchR = batchA + batchB
    batchX = batchR + batchA
    for i, (a, b) in enumerate(zip(A, B)):
        r = batchR[i]
        assert abs(a + b - r) <= 0.1

    for i, a in enumerate(A):
        r = batchR[i]
        x = batchX[i]
        assert abs(r + a - x) <= 1e-5


def test_signed_batchnumber():
    A = [0.3, 2.7, 4.6, -3.2, 1.2, -7.4]
    B = [4.5, -2.0, 3.1, 1.24, 3.3, 5.8]
    size = 32

    quantizer = SignedBatchNumber.quantizer()
    quantizer.set_float_range(-20.0, 20.0)
    quantizer.set_int_size(size)
    quantizer.compile()

    batchA = SignedBatchNumber.bind(*A, bit_length=size)
    batchB = SignedBatchNumber.bind(*B, bit_length=size)

    batchR = batchA + batchB
    batchX = batchR + batchA
    for i, (a, b) in enumerate(zip(A, B)):
        r = batchR[i]
        assert abs(r - (a + b)) <= 1e-6

    for i, a in enumerate(A):
        r = batchR[i]
        x = batchX[i]
        assert abs(x - (r + a)) <= 1e-6


if __name__ == "__main__":
    test_signed_batchnumber()
