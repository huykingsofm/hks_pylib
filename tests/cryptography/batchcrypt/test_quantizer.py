import random

from hks_pylib.cryptography.batchcrypt.quantization import Quantizer

from hks_pylib.errors.cryptography.batchcrypt.integer import OverflowIntegerError
from hks_pylib.errors.cryptography.batchcrypt.quantization import OverflowQuantizerError


def test_generic_quantizer():
    frange = 1.0
    isize = 16

    quantizer = Quantizer()
    quantizer.set_float_range(-frange, frange)
    quantizer.set_int_size(isize, signed=False)
    quantizer.compile()

    f1 = random.randint(-frange*100, frange*100) / 100
    f2 = random.randint(-frange*100, frange*100) / 100
    
    i1 = quantizer.f2i(f1)
    i2 = quantizer.f2i(f2)

    isum = i1 + i2

    try:
        dfsum = quantizer.i2f(isum, n_cumulative=2)

        if f1 + f2 < -frange or f1 + f2 > frange:
            assert False

        assert abs(dfsum - (f1 + f2)) <= 1e-2
    except OverflowQuantizerError:
        if f1 + f2 >= -frange and f1 + f2 <= frange:
            assert False


def test_signed_quantizer():
    frange = 1.0
    isize = 16

    quantizer = Quantizer()
    quantizer.set_float_range(-frange, frange)
    quantizer.set_int_size(isize, signed=True)
    quantizer.compile()

    f1 = random.randint(-frange*100, frange*100) / 100
    f2 = random.randint(-frange*100, frange*100) / 100
    
    i1 = quantizer.f2i(f1)
    i2 = quantizer.f2i(f2)

    try:
        isum = i1 + i2
        dfsum = quantizer.i2f(isum)
        
        if f1 + f2 < -frange or f1 + f2 > frange:
            assert False

        assert abs(dfsum - (f1 + f2)) <= 1e-2
    except (OverflowIntegerError, OverflowQuantizerError):
        if f1 + f2 >= -frange and f1 + f2 <= frange:
            assert False


if __name__ == "__main__":
    test_generic_quantizer()