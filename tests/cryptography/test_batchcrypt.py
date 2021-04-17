from hks_pylib.cryptography.batchcrypt.batchnumber import BatchNumber
from hks_pylib.cryptography.batchcrypt.quantization import F2IQuantizer, QuantizedBatchNumber
from hks_pylib.errors import InvalidElementError

def test_batchnumber():
    a = BatchNumber.bind(2, 3, 4, bit_length=8)
    b = BatchNumber.bind(2, 4, 6, bit_length=8)

    assert a.get(0) == 2
    assert a.get(1) == 3
    assert a.get(2) == 4

    try:
        a.get(3)
        assert False
    except InvalidElementError:
        pass

    assert b[0] == 2
    assert b[1] == 4
    assert b[2] == 6

    c = a + b
    assert c.get(0) == 4
    assert c.get(1) == 7
    assert c.get(2) == 10


def test_quantizer():
    quantizer = F2IQuantizer()
    quantizer.set_float_range(-100.0, 200.0)
    quantizer.set_int_size(32)
    quantizer.compile()
    
    f = 0.8
    i = quantizer.f2i(f)
    fd = quantizer.i2f(i)
    assert fd - f < 1


def test_across():
    A = [0.3, 2.7, 4.6, -3.2, 1.2, -7.4]
    B = [4.5, -2.0, 3.1, 1.24, 3.3, 5.8]

    quantizer = QuantizedBatchNumber.quantizer()
    quantizer.set_float_range(-13.0, 13.0)
    quantizer.set_int_size(16)
    quantizer.compile()

    batchA = QuantizedBatchNumber.bind(*A, bit_length=16)
    batchB = QuantizedBatchNumber.bind(*B, bit_length=16)

    batchR = batchA + batchB
    batchX = batchR + batchA
    for i, (a, b) in enumerate(zip(A, B)):
        r = batchR[i]
        assert a + b - r <= 0.1

    for i, a in enumerate(A):
        r = batchR[i]
        x = batchX[i]
        assert r + a - x <= 1e-3

if __name__ == "__main__":
    test_across()
