from hks_pylib.cryptography.batchcrypt.batchnumber import BatchNumber
from hks_pylib.errors import InvalidParameterError, NotCompileQuatizerError, NotSetRangeOfQuantizer, OutOfRangeQuantizerError
from hks_pylib.math import Bitwise


class F2IQuantizer(object):
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

    def set_int_range(self, min_value: int, max_value: int): 
        if not isinstance(min_value, int):
            raise InvalidParameterError("Parameter min_value must be a int.")

        if not isinstance(max_value, int):
            raise InvalidParameterError("Parameter max_value must be a int.")

        if min_value >= max_value:
            raise InvalidParameterError("Parameter min_value must be "
            "less than max_value.")

        self.__int_range = (min_value, max_value)

    def set_int_size(self, size_in_bit: int, signed: bool = False):
        if not isinstance(size_in_bit, int):
            raise InvalidParameterError("Parameter size_int_bit must be a int.")
        
        if size_in_bit <= 0:
            raise InvalidParameterError("Parameter size_in_bit must be a "
            "positive number.")

        max_value = Bitwise.get_max_number(size_in_bit)
        min_value = 0
        if signed:
            min_value = - max_value // 2
            max_value = max_value // 2 + 1

        self.__int_range = (min_value, max_value)

    def compile(self):
        if self.__int_range is None:
            raise NotSetRangeOfQuantizer("Please set int range "
            "or int size before calling compile().")
        
        if self.__float_range is None:
            raise NotSetRangeOfQuantizer("Please set float range "
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
            raise OutOfRangeQuantizerError("Value is out of range "
            "(expected {} <= f <= {}).".format(
                self.__float_range[0], self.__float_range[1]))

        return int(self.__scale * f + self.__offset)

    def i2f(self, i: float, force: bool = False, n_cumulative: int = 1):
        if not isinstance(i, int):
            raise InvalidParameterError("Parameter i must be a int.")
        
        if not isinstance(n_cumulative, int) or n_cumulative < 1:
            raise InvalidParameterError("Parameter n_cummulative must be\
                a int and greater than 0.")
        
        if self.__offset is None or self.__scale is None:
            raise NotCompileQuatizerError("Please calling compile() before.")

        i = i - (n_cumulative - 1) * self.__offset

        if not force and\
            (i < self.__int_range[0] or i > self.__int_range[1]):
            raise OutOfRangeQuantizerError("Value is out of range "
            "(expected {} <= i <= {}).".format(
                self.__int_range[0], self.__int_range[1]))

        return (i - self.__offset) / self.__scale


class QuantizedBatchNumber(BatchNumber):
    __quantizer = F2IQuantizer()
    def __init__(self, number: int, n_elements: int, element_length: int) -> None:
        super().__init__(number, n_elements, element_length)
        self._n_cumulative = 1
    
    @staticmethod
    def quantizer():
        return QuantizedBatchNumber.__quantizer

    def __add__(self, other: BatchNumber):
        result = super().__add__(other)
        result = QuantizedBatchNumber(
            result._number,
            result._n_elements,
            result._element_length
        )
        result._n_cumulative = self._n_cumulative + other._n_cumulative
        return result
    
    def __iadd__(self, other: BatchNumber):
        super().__iadd__(other)
        self._n_cumulative += other._n_cumulative

    def get(self, index: int) -> int:
        result = super().get(index)
        return self.__quantizer.i2f(result, n_cumulative=self._n_cumulative)

    @staticmethod
    def bind(*numbers, bit_length: int):
        numbers = (QuantizedBatchNumber.__quantizer.f2i(f) for f in numbers)
        result = BatchNumber.bind(*numbers, bit_length=bit_length)
        return QuantizedBatchNumber(result._number, result._n_elements, result._element_length)
