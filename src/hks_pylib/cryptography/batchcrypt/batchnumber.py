from hks_pylib.cryptography.batchcrypt.integer import SignedInteger
from hks_pylib.errors import InvalidParameterError
from hks_pylib.math import Bitwise
from hks_pylib.cryptography.batchcrypt.quantization import GenericQuantizer, SignedQuantizer

from hks_pylib.errors.cryptography.batchcrypt.batchnumber import *

class BatchNumber(object):
    PADDING_SIZE = 2

    def __init__(
                self,
                batch: int,
                num: int,   # the number of elements in the batch
                size: int   # the size of each element in the batch
            ) -> None:
        self._num = num
        self._size = size
        self._total_size = size + BatchNumber.PADDING_SIZE

        self._batch = batch
        self._batch_size = self._num * self._total_size

    def get(self, index: int) -> int:
        if not isinstance(index, int):
            raise InvalidElementBatchNumberError("Parameter index must be an int.")

        if index >= self._num or index < 0:
            raise InvalidElementBatchNumberError("You can only access elements "
            "starting from 0 to {}".format(self._num - 1))

        return Bitwise.get_bits(
                number=self._batch,
                position=self._batch_size\
                    - index * self._total_size - 1,
                length=self._total_size
            )

    def __getitem__(self, index: int):
        return self.get(index)

    def __len__(self):
        return self._num

    def size(self):
        return self._size

    def total_size(self):
        return self._total_size

    def __add__(self, other):
        if not isinstance(other, type(self)):
            return InvalidParameterError("Two operands "
            "must be the same type ({} != {}).".format(type(self), type(other)))

        if self._num != other._num:
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same number of elements ({} != {}).".format(
                    self._num,
                    other._num
                ))

        if self._total_size != other._total_size:
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same element length ({} != {}).".format(
                    self._total_size,
                    other._total_size
                ))

        return BatchNumber(
                self._batch + other._batch,
                self._num,
                self._size
            )

    
    def __iadd__(self, other):
        if not isinstance(other, type(self)):
            return InvalidParameterError("Two operands "
            "must be the same type ({} != {}).".format(type(self), type(other)))

        if self._num != other._num:
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same number of elements ({} != {}).".format(
                    self._num,
                    other._num
                ))

        if self._total_size != other._total_size:
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same element length ({} != {}).".format(
                    self._total_size,
                    other._total_size
                ))

        self._batch += other._batch

    def __str__(self) -> str:
        return bin(self._batch)

    def __repr__(self) -> str:
        return str(self)
    
    def to_int(self) -> int:
        return self._batch

    @staticmethod
    def bind(*numbers, size: int = 8):
        total_size = size + BatchNumber.PADDING_SIZE

        batch_length = total_size * len(numbers)
        batch = 0

        for i, number in enumerate(numbers):
            batch = Bitwise.set_bits(
                    number=batch,
                    position=batch_length - total_size * i\
                        - BatchNumber.PADDING_SIZE - 1,
                    length=size,
                    value=number
                )

        return BatchNumber(batch, len(numbers), size)



class GenericBatchNumber(BatchNumber):
    __quantizer = GenericQuantizer()
    def __init__(self, batch: int, num: int, size: int) -> None:
        super().__init__(batch, num, size)
        self._n_cumulative = 1
    
    @staticmethod
    def quantizer():
        return GenericBatchNumber.__quantizer

    def __add__(self, other: BatchNumber):
        if not isinstance(other, GenericBatchNumber):
            raise InvalidParameterError("Operands of addition "
            "must be GenericBatchNumber objects.")

        result = super().__add__(other)
        result = GenericBatchNumber(
                result._batch,
                result._num,
                result._size
            )
        result._n_cumulative = self._n_cumulative + other._n_cumulative
        return result
    
    def __iadd__(self, other: BatchNumber):
        if not isinstance(other, GenericBatchNumber):
            raise InvalidParameterError("Operands of addition "
            "must be GenericBatchNumber objects.")

        super().__iadd__(other)
        self._n_cumulative += other._n_cumulative

    def get(self, index: int) -> int:
        result = super().get(index)
        return self.__quantizer.i2f(result, n_cumulative=self._n_cumulative)

    @staticmethod
    def bind(*numbers, size: int):
        numbers = (GenericBatchNumber.__quantizer.f2i(f) for f in numbers)
        result = BatchNumber.bind(*numbers, size=size)
        return GenericBatchNumber(result._batch, result._num, result._size)


class SignedBatchNumber(BatchNumber):
    __quantizer = SignedQuantizer()

    def __init__(self, batch: int, num: int, size: int) -> None:
        super().__init__(batch, num, size)
        self._original_size = size - SignedInteger.sign_size() + 1

    @staticmethod
    def quantizer():
        return SignedBatchNumber.__quantizer

    @staticmethod
    def bind(*numbers, size: int):
        signed_numbers = []
        for n in numbers:
            sn = SignedBatchNumber.__quantizer.f2i(n)
            signed_numbers.append(sn.to_int())

        raw_result = BatchNumber.bind(
                *signed_numbers, 
                size=SignedInteger.total_size_(size)
            )
        result = SignedBatchNumber(
                batch=raw_result._batch,
                num=raw_result._num,
                size=raw_result._size
            )
        return result

    def get(self, index: int) -> int:
        raw_result = super().get(index)
        signed_number = SignedInteger(
                number=raw_result,
                original_size=self._original_size
            )
        return self.__quantizer.i2f(signed_number)

    def __add__(self, other: BatchNumber):
        raw_result = super().__add__(other)
        return SignedBatchNumber(
                batch=raw_result._batch,
                num=raw_result._num,
                size=raw_result._size
            )
