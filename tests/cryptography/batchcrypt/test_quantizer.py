import random

from hks_pylib.cryptography.batchcrypt.quantization import SignedQuantizer
from hks_pylib.cryptography.batchcrypt.quantization import GenericQuantizer

from hks_pylib.errors.cryptography.batchcrypt.integer import OverflowIntegerError
from hks_pylib.errors.cryptography.batchcrypt.quantization import OverflowQuantizerError

def test_generic_quantizer():
    frange = (-1.0, 1.0)
    isize = 8
    signed = True

    quantizer = GenericQuantizer()
    quantizer.set_float_range(*frange)
    quantizer.set_int_size(isize, signed=signed)
    quantizer.compile()

    f1 = random.randint(-100, 100) / 100
    f2 = random.randint(-100, 100) / 100
    print("f1", f1)
    print("f2", f2)
    
    i1 = quantizer.f2i(f1)
    print("i1", i1)
    i2 = quantizer.f2i(f2)
    print("i2", i2)

    isum = i1 + i2

    try:
        dfsum = quantizer.i2f(isum)

        if f1 + f2 < frange[0] or f1 + f2 > frange[1]:
            assert False

        assert abs(dfsum - (f1 + f2)) <= 1e-2
    except OverflowQuantizerError:
        if f1 + f2 >= frange[0] and f1 + f2 <= frange[1]:
            assert False

def test_signed_quantizer():
    frange = (-1.0, 1.0)
    isize = 8

    quantizer = SignedQuantizer()
    quantizer.set_float_range(*frange)
    quantizer.set_int_size(isize)
    quantizer.compile()

    f1 = random.randint(-100, 100) / 100
    f2 = random.randint(-100, 100) / 100
    print("f1", f1)
    print("f2", f2)
    
    i1 = quantizer.f2i(f1)
    print("i1", i1.value())
    i2 = quantizer.f2i(f2)
    print("i2", i2.value())

    try:
        isum = i1 + i2
        
        if f1 + f2 < frange[0] or f1 + f2 > frange[1]:
            assert False
        
        dfsum = quantizer.i2f(isum)
        assert abs(dfsum - (f1 + f2)) <= 1e-2
    except OverflowIntegerError:
        if f1 + f2 >= frange[0] and f1 + f2 <= frange[1]:
            assert False
    