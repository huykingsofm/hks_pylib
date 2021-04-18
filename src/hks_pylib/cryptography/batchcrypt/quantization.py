from hks_pylib.cryptography.batchcrypt.integer import SignedInteger
from hks_pylib.math import Bitwise

from hks_pylib.errors import InvalidParameterError
from hks_pylib.errors.cryptography.batchcrypt.quantization import *


class GenericQuantizer(object):
    def __init__(self) -> None:
        self.__float_range = None
        self.__int_range = None

        self.__scale = None
        self.__offset = None
    
    def set_float_range(self, min_value: float, max_value: float):
        if not isinstance(min_value, float):
            raise InvalidParameterError("Parameter min_value must be a float.")

        if not isinstance(max_value, float):
            raise InvalidParameterError("Parameter max_value must be a float.")

        if min_value >= max_value:
            raise InvalidParameterError("Parameter min_value must be less than max_value.")

        self.__float_range = (min_value, max_value)

    def set_int_size(self, size_in_bit: int, signed: bool = False):
        if not isinstance(size_in_bit, int):
            raise InvalidParameterError("Parameter size_in_bit must be an int.")
        
        if size_in_bit <= 0:
            raise InvalidParameterError("Parameter size_in_bit must be an "
            "positive number.")

        if not signed:
            max_value = Bitwise.get_max_number(size_in_bit)
            min_value = 0

        else:
            max_value = Bitwise.get_max_number(size_in_bit - 1)
            min_value = -max_value

        self.__int_range = (min_value, max_value)

    def compile(self):
        if self.__int_range is None:
            raise NotSetRangeOfQuantizerError("Please set "
            "int size before calling compile().")
        
        if self.__float_range is None:
            raise NotSetRangeOfQuantizerError("Please set float range "
            "before calling compile().")

        maxi, mini = self.__int_range
        maxf, minf = self.__float_range
        self.__scale = (maxi - mini) / (maxf - minf)
        self.__offset = (maxf * mini - maxi * minf) / (maxf - minf)

    def f2i(self, f: float, force: bool = False):
        if not isinstance(f, float):
            raise InvalidParameterError("Parameter f must be a float.")
        
        if self.__offset is None or self.__scale is None:
            raise NotCompileQuatizerError("Please calling compile() before.")

        if not force and\
            (f < self.__float_range[0] or f > self.__float_range[1]):
            raise OverflowQuantizerError("Value is out of range "
            "(expected {} <= f <= {}).".format(
                self.__float_range[0],
                self.__float_range[1]
            ))

        return int(self.__scale * f + self.__offset)

    def i2f(self, i: int, force: bool = False, n_cumulative: int = 1):
        if not isinstance(i, int):
            raise InvalidParameterError("Parameter i must be an int.")
        
        if not isinstance(n_cumulative, int) or n_cumulative < 1:
            raise InvalidParameterError("Parameter n_cummulative must be\
                a int and greater than 0.")
        
        if self.__offset is None or self.__scale is None:
            raise NotCompileQuatizerError("Please calling compile() before.")

        i = i - (n_cumulative - 1) * self.__offset

        if not force and\
            (i < self.__int_range[0] or i > self.__int_range[1]):
            raise OverflowQuantizerError("Value is out of range "
            "(expected {} <= i <= {}).".format(
                self.__int_range[0],
                self.__int_range[1]
            ))

        return (i - self.__offset) / self.__scale

class SignedQuantizer(GenericQuantizer):
    def __init__(self) -> None:
        super().__init__()
        self.__size = None

    def set_float_range(self, min_value: float, max_value: float):
        if min_value + max_value != 0:
            raise InvalidParameterError("BatchCrypt Quantization "
            "require range of float to be symmetric.")

        super().set_float_range(min_value, max_value)

    def set_int_size(self, size_in_bit: int):
        super().set_int_size(size_in_bit, signed=True)
        self.__size = size_in_bit

    def compile(self):
        super().compile()

    def f2i(self, f: float, force: bool = False) -> SignedInteger:
        raw_result = super().f2i(f, force=force)
        result = SignedInteger.from_int(raw_result, self.__size)
        return result

    def i2f(self, i: SignedInteger, force: bool = False) -> float:
        if not isinstance(i, SignedInteger):
            raise InvalidParameterError("Parameter i must be a SignedInteger object.")

        i = i.value()

        return super().i2f(i, force=force, n_cumulative=1)