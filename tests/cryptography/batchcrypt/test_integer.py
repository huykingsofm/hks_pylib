import random

from hks_pylib.math import Bitwise

from hks_pylib.cryptography.batchcrypt.integer import SignedInteger
from hks_pylib.errors.cryptography.batchcrypt.integer import OverflowIntegerError


def test_integer():
    size = 8
    range_value = Bitwise.max_natural_number(size - SignedInteger.sign_size())


    sample_a = random.randint(-range_value, range_value)
    sample_b = random.randint(-range_value, range_value)

    a = SignedInteger.from_int(sample_a, size)
    b = SignedInteger.from_int(sample_b, size)

    assert a.value() == sample_a
    assert b.value() == sample_b

    try:
        add = a + b
        if sample_a + sample_b < -range_value or sample_a + sample_b > range_value:
            assert False

        assert add == sample_a + sample_b
    except OverflowIntegerError:
        if -range_value < sample_a + sample_b and sample_a + sample_b < range_value:
            assert False

    try:
        sub = a - b
        if sample_a - sample_b < -range_value or sample_a - sample_b > range_value:
            assert False

        assert sub == sample_a - sample_b
    except OverflowIntegerError:
        if -range_value < sample_a - sample_b and sample_a - sample_b < range_value:
            assert False

    #mul = a * b
    #print("mul", bin(mul.to_int()), mul.value())


if __name__ == "__main__":
    test_integer()