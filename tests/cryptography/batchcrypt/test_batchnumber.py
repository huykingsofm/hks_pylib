import random

from hks_pylib.cryptography.batchcrypt.batchnumber import GenericBatchNumber
from hks_pylib.cryptography.batchcrypt.batchnumber import BatchNumber, SignedBatchNumber

from hks_pylib.errors.cryptography.batchcrypt.integer import *
from hks_pylib.errors.cryptography.batchcrypt.batchnumber import *
from hks_pylib.errors.cryptography.batchcrypt.quantization import OverflowQuantizerError


def test_batchnumber():
    a = BatchNumber.bind(2, 3, 4, size=8)
    b = BatchNumber.bind(2, 4, 6, size=8)

    assert a.get(0) == 2
    assert a.get(1) == 3
    assert a.get(2) == 4

    try:
        a.get(3)
        assert False
    except BatchNumberError:
        pass

    assert b[0] == 2
    assert b[1] == 4
    assert b[2] == 6

    c = a + b
    assert c.get(0) == 4
    assert c.get(1) == 7
    assert c.get(2) == 10


def test_generic_batchnumber():
    frange = (-20.0, 20.1)
    isize = 32
    epsilon = 1e-5

    random_float = lambda l, h: random.randint(int(l * 1000), int(h * 1000)) / 1000
    A = [random_float(frange[0] + 10, frange[1] - 10) for _ in range(10)]
    B = [random_float(frange[0] + 10, frange[1] - 10) for _ in range(10)]

    # For debugging
    #A = [3.832, 8.59, -3.483, -6.702, 8.706, -7.674, -8.124, 9.186, -0.067, 3.017]
    #B = [-5.032, 3.183, -4.383, 5.589, 6.519, -9.281, 3.996, -3.245, -8.343, -8.723]

    GenericBatchNumber.quantizer(
        float_range=frange,
        int_size=isize
    )

    batchA = GenericBatchNumber.bind(*A, size=isize)
    assert abs(batchA[0] - A[0]) <= epsilon

    batchB = GenericBatchNumber.bind(*B, size=isize)
    assert abs(batchB[0] - B[0]) <= epsilon

    batchR = batchA + batchB
    batchX = batchR + batchA
    for i, (a, b) in enumerate(zip(A, B)):
        try:
            r = batchR[i]

            if r < frange[0] or r > frange[1]:
                print("a={}, b={}, r={}".format(a, b, r))
                print(A, B)
                assert False
            assert abs(a + b - r) <= epsilon
        except OverflowQuantizerError:
            if frange[0] <= a + b and a + b <= frange[1]:
                print("a={}, b={}, r={}".format(a, b, r))
                print(A, B)
                assert False

    for i, a in enumerate(A):
        try:
            r = batchR[i]
            x = batchX[i]

            if x < frange[0] or x > frange[1]:
                print("a={}, b={}, r={}, x={}".format(a, B[i], r, x))
                print(A, B)
                assert False

            assert abs(r + a - x) <= epsilon
        except OverflowQuantizerError:
            if frange[0] <= a + r and a + r <= frange[1]:
                print("a={}, b={}, r={}, x={}".format(a, B[i], r, x))
                print(A, B)
                assert False


def test_signed_batchnumber():
    frange = (-20.0, 20.0)
    isize = 32
    epsilon = 1e-5

    random_float = lambda l, h: random.randint(int(l * 1000), int(h * 1000)) / 1000
    A = [random_float(frange[0] + 10, frange[1] - 10) for _ in range(10)]
    B = [random_float(frange[0] + 10, frange[1] - 10) for _ in range(10)]

    # For debugging
    #A = [6.367, 8.59, -3.483, -6.702, 8.706, -7.674, -8.124, 9.186, -0.067, 3.017]
    #B = [7.441, 3.183, -4.383, 5.589, 6.519, -9.281, 3.996, -3.245, -8.343, -8.723]

    SignedBatchNumber.quantizer(
        float_range=frange,
        int_size= isize
    )

    batchA = SignedBatchNumber.bind(*A, size=isize)
    assert abs(batchA[0] - A[0]) <= epsilon

    batchB = SignedBatchNumber.bind(*B, size=isize)
    assert abs(batchB[0] - B[0]) <= epsilon

    batchR = batchA + batchB
    batchX = batchR + batchA
    for i, (a, b) in enumerate(zip(A, B)):
        try:
            r = batchR[i]

            if r < frange[0] or r > frange[1]:
                print("a={}, b={}, r={}".format(a, b, r))
                print(A, B)
                assert False
            assert abs(a + b - r) <= epsilon
        except OverflowQuantizerError:
            if frange[0] <= a + b and a + b <= frange[1]:
                print("a={}, b={}, r={}".format(a, b, r))
                print(A, B)
                assert False

    for i, a in enumerate(A):
        try:
            r = batchR[i]
            x = batchX[i]

            if x < frange[0] or x > frange[1]:
                print("a={}, b={}, r={}, x={}".format(a, B[i], r, x))
                print(A, B)
                assert False

            assert abs(r + a - x) <= epsilon
        except (OverflowQuantizerError, OverflowIntegerError):
            if frange[0] <= a + r and a + r <= frange[1]:
                print("a={}, b={}, r={}, x={}".format(a, B[i], r, x))
                print(A, B)
                assert False


if __name__ == "__main__":
    test_signed_batchnumber()
