from hks_pylib.math import Bitwise

from hks_pylib.cryptography.batchcrypt.integer import SignedInteger
from hks_pylib.cryptography.batchcrypt.quantization import Quantizer

from hks_pylib.errors import InvalidParameterError
from hks_pylib.errors.cryptography.batchcrypt.batchnumber import *
from hks_pylib.errors.cryptography.batchcrypt.integer import OverflowIntegerError


class BatchNumber(object):
    __PADDING_SIZE = 2

    @staticmethod
    def padding_size():
        return BatchNumber.__PADDING_SIZE

    @staticmethod
    def set_padding_size(value: int):
        if not isinstance(value, int) or value < 0:
            raise InvalidParameterError("Padding size must be a "
            "positive int.")

        BatchNumber.__PADDING_SIZE = value

    def __init__(
                self,
                batch: int,
                num: int,   # the number of values in the batch
                size: int   # the size of each values in the batch
            ) -> None:
        self._num = num
        self._value_size = size
        self._element_size = size + BatchNumber.padding_size()

        self._raw = batch
        self._total_size = self._num * self._element_size

    def get(self, index: int) -> int:
        if not isinstance(index, int):
            raise InvalidElementBatchNumberError("Parameter index must be an int.")

        if index >= len(self) or index < 0:
            raise InvalidElementBatchNumberError("You can only access elements "
            "starting from 0 to {}".format(len(self) - 1))

        return Bitwise.get_bits(
                number=self.raw(),
                position=self.total_size()\
                    - index * self.element_size() - 1,
                length=self.element_size()
            )

    def __getitem__(self, index: int):
        return self.get(index)

    def __len__(self):
        return self._num

    def value_size(self):
        "Only the size of value without padding bits."
        return self._value_size

    def element_size(self):
        "Including both value size and padding size."
        return self._element_size

    def total_size(self):
        return self._total_size

    def raw(self):
        return self._raw

    def __add__(self, other):
        if not isinstance(other, type(self)):
            return InvalidParameterError("Two operands "
            "must be the same type ({} != {}).".format(
                type(self).__name__, type(other).__name__))

        if len(self) != len(other):
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same number of elements ({} != {}).".format(
                    len(self),
                    len(other)
                ))

        if self.element_size() != other.element_size():
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same element length ({} != {}).".format(
                    self.element_size(),
                    other.element_size()
                ))

        return BatchNumber(
                self.raw() + other.raw(),
                len(self),
                self.value_size()
            )

    
    def __iadd__(self, other):
        if not isinstance(other, type(self)):
            return InvalidParameterError("Two operands "
            "must be the same type ({} != {}).".format(
                type(self).__name__, type(other).__name__))

        if len(self) != len(other):
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same number of elements ({} != {}).".format(
                    len(self),
                    len(other)
                ))

        if self.element_size() != other.element_size():
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same element length ({} != {}).".format(
                    self.element_size(),
                    other.element_size()
                ))

        self._raw += other.raw()

    def __len__(self):
        return self._num

    def __str__(self) -> str:
        return bin(self._raw)

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def bind(*numbers, size: int):
        element_size = size + BatchNumber.padding_size()

        total_size = element_size * len(numbers)
        raw = 0

        for i, number in enumerate(numbers):
            raw = Bitwise.set_bits(
                    number=raw,
                    position=total_size - element_size * i\
                        - BatchNumber.padding_size() - 1,
                    length=size,
                    value=number
                )

        return BatchNumber(raw, len(numbers), size)


class GenericBatchNumber(BatchNumber):
    __quantizer = Quantizer()
    def __init__(self, batch: int, num: int, size: int) -> None:
        super().__init__(batch, num, size)
        self._n_cumulative = 1
    
    @staticmethod
    def quantizer(float_range: tuple, int_size: int):
        GenericBatchNumber.__quantizer.set_float_range(*float_range)
        GenericBatchNumber.__quantizer.set_int_size(int_size, signed=False)
        GenericBatchNumber.__quantizer.compile()

    @staticmethod
    def bind(*numbers, size: int):
        numbers = (GenericBatchNumber.__quantizer.f2i(f) for f in numbers)
        result = BatchNumber.bind(*numbers, size=size)
        return GenericBatchNumber(result._raw, result._num, result.value_size())

    def get(self, index: int) -> int:
        result = super().get(index)
        return self.__quantizer.i2f(result, n_cumulative=self._n_cumulative)

    def __add__(self, other: BatchNumber):
        if not isinstance(other, type(self)):
            raise InvalidParameterError("Operands of addition "
            "must be {} objects.".format(type(self).__name__))

        result = super().__add__(other)
        result = GenericBatchNumber(
                result.raw(),
                len(result),
                result.value_size()
            )
        result._n_cumulative = self._n_cumulative + other._n_cumulative
        return result

    def __iadd__(self, other: BatchNumber):
        if not isinstance(other, type(self)):
            raise InvalidParameterError("Operands of addition "
            "must be {} objects.".format(type(self).__name__))

        super().__iadd__(other)
        self._n_cumulative += other._n_cumulative


class SignedBatchNumber(BatchNumber):
    __quantizer = Quantizer()

    def __init__(self, batch: int, num: int, size: int) -> None:
        super().__init__(batch, num, size)

    @staticmethod
    def quantizer(float_range: tuple, int_size: int):
        if not isinstance(float_range, tuple) or len(float_range) != 2\
            or sum(float_range) != 0:
            raise InvalidParameterError("Float range "
            "in signed batch number must be symmetric")

        SignedBatchNumber.__quantizer.set_float_range(*float_range)
        SignedBatchNumber.__quantizer.set_int_size(
                int_size - SignedInteger.sign_size() + 1,
                signed=True
            )
        SignedBatchNumber.__quantizer.compile()

    @staticmethod
    def bind(*fnumbers, size: int):
        signed_number_list = []
        for f in fnumbers:
            i = SignedBatchNumber.__quantizer.f2i(f)
            signed_number: SignedInteger = SignedInteger.from_int(i, size)
            signed_number_list.append(signed_number.raw())

        super_result = BatchNumber.bind(
                *signed_number_list, 
                size=size
            )

        result = SignedBatchNumber(
                batch=super_result.raw(),
                num=len(super_result),
                size=super_result.value_size()
            )
        return result

    def get(self, index: int) -> int:
        raw_result = super().get(index)
        try:
            signed_number = SignedInteger(
                    number=raw_result,
                    size=self.value_size()
                )
        except OverflowIntegerError as e:
            raise e

        return self.__quantizer.i2f(signed_number.value())

    def __add__(self, other: BatchNumber):
        raw_result = super().__add__(other)
        return SignedBatchNumber(
                batch=raw_result.raw(),
                num=len(raw_result),
                size=raw_result.value_size()
            )
