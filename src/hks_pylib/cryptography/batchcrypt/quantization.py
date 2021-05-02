from hkserror.hkserror import HFormatError, HTypeError
from hks_pylib.math import Bitwise

from hks_pylib.errors.cryptography.batchcrypt.quantization import *


class Quantizer(object):
    def __init__(self) -> None:
        self.__float_range = None
        self.__int_range = None

        self.__scale = None
        self.__offset = None
    
    def set_float_range(self, min_value: float, max_value: float):
        if not isinstance(min_value, float):
            raise HTypeError("min_value", min_value, float)

        if not isinstance(max_value, float):
            raise HTypeError("max_value", max_value, float)

        if min_value >= max_value:
            raise HFormatError("Parameter min_value must be less than max_value.")

        self.__float_range = (min_value, max_value)

    def set_int_size(self, size_in_bit: int, signed: bool = False):
        if not isinstance(size_in_bit, int):
            raise HTypeError("size_in_bit", size_in_bit, int)

        if size_in_bit <= 0:
            raise HFormatError("Parameter size_in_bit must be an "
            "positive number.")

        if not signed:
            max_value = Bitwise.max_natural_number(size_in_bit)
            min_value = 0

        else:
            max_value = Bitwise.max_natural_number(size_in_bit - 1)
            min_value = -max_value

        self.__int_range = (min_value, max_value)

    def compile(self):
        if self.__int_range is None:
            raise RangeOfQuantizerError("Please set "
            "int size before calling compile().")
        
        if self.__float_range is None:
            raise RangeOfQuantizerError("Please set "
            "float range before calling compile().")

        maxi, mini = self.__int_range
        maxf, minf = self.__float_range
        self.__scale = (maxi - mini) / (maxf - minf)
        self.__offset = (maxf * mini - maxi * minf) / (maxf - minf)

    def f2i(self, f: float, force: bool = False):
        if not isinstance(f, float):
            raise HTypeError("f", f, float)
        
        if self.__offset is None or self.__scale is None:
            raise QuantizerError("Please calling compile() before.")

        if not force and\
            (f < self.__float_range[0] or f > self.__float_range[1]):
            raise OverflowQuantizerError("Float value is out of range "
            "(expected {} <= f <= {}).".format(
                self.__float_range[0],
                self.__float_range[1]
            ))

        return int(self.__scale * f + self.__offset)

    def i2f(self, i: int, force: bool = False, n_cumulative: int = 1):
        if not isinstance(i, int):
            raise HTypeError("i", i, int)
        
        if not isinstance(n_cumulative, int):
            raise HTypeError("n_cummulative", n_cumulative, int)
        
        if n_cumulative < 1:
            raise HFormatError("Parameter n_cummulative expected an positive integer.")
        
        if self.__offset is None or self.__scale is None:
            raise QuantizerError("Please calling compile() before.")

        i = i - (n_cumulative - 1) * self.__offset

        if not force and\
            (i < self.__int_range[0] or i > self.__int_range[1]):
            raise OverflowQuantizerError("Int value is out of range "
            "(expected {} <= i <= {}).".format(
                self.__int_range[0],
                self.__int_range[1]
            ))

        return (i - self.__offset) / self.__scale
