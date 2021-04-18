from hks_pylib.cryptography.batchcrypt.integer import SignedInteger
from hks_pylib.errors import InvalidParameterError
from hks_pylib.math import Bitwise
from hks_pylib.cryptography.batchcrypt.quantization import GenericQuantizer, SignedQuantizer

from hks_pylib.errors.cryptography.batchcrypt.batchnumber import *

class BatchNumber(object):
    PADDING_LENGTH = 2

    def __init__(
                self,
                batch: int,
                n_elements: int,
                element_length: int
            ) -> None:
        self._n_elements = n_elements
        self._element_length = element_length

        self._batch = batch
        self._batch_length = self._n_elements * self._element_length

    def get(self, index: int) -> int:
        if not isinstance(index, int):
            raise InvalidElementBatchNumberError("Parameter index must be an int.")

        if index >= self._n_elements or index < 0:
            raise InvalidElementBatchNumberError("You can only access elements "
            "starting from 0 to {}".format(self._n_elements - 1))

        return Bitwise.get_bits(
            number=self._batch,
            position=self._batch_length\
                - index * self._element_length - 1,
            length=self._element_length
        )

    def __getitem__(self, index: int):
        return self.get(index)

    def __len__(self):
        return self._n_elements

    def __add__(self, other):
        if not isinstance(other, type(self)):
            return InvalidParameterError("Two operands "
            "must be the same type ({} != {}).".format(type(self), type(other)))

        if self._n_elements != other._n_elements:
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same number of elements ({} != {}).".format(
                self._n_elements,
                other._n_elements
            ))

        if self._element_length != other._element_length:
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same element length ({} != {}).".format(
                self._element_length,
                other._element_length
            ))

        return BatchNumber(
            self._batch + other._batch,
            self._n_elements,
            self._element_length
        )

    
    def __iadd__(self, other):
        if not isinstance(other, type(self)):
            return InvalidParameterError("Two operands "
            "must be the same type ({} != {}).".format(type(self), type(other)))

        if self._n_elements != other._n_elements:
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same number of elements ({} != {}).".format(
                self._n_elements,
                other._n_elements
            ))

        if self._element_length != other._element_length:
            raise MismatchedTypeBatchNumberError("Two operands "
            "must be the same element length ({} != {}).".format(
                self._element_length,
                other._element_length
            ))

        self._batch += other._batch

    def __str__(self) -> str:
        return bin(self._batch)

    def __repr__(self) -> str:
        return str(self)
    
    def to_int(self) -> int:
        return self._batch

    @staticmethod
    def bind(*numbers, bit_length: int = 8):
        element_length = bit_length + BatchNumber.PADDING_LENGTH

        batch_length = element_length * len(numbers)
        batch = 0

        for i, number in enumerate(numbers):
            batch = Bitwise.set_bits(
                number=batch,
                position=batch_length - element_length * i\
                    - BatchNumber.PADDING_LENGTH - 1,
                length=bit_length,
                value=number
            )

        return BatchNumber(batch, len(numbers), element_length)



class GenericBatchNumber(BatchNumber):
    __quantizer = GenericQuantizer()
    def __init__(self, number: int, n_elements: int, element_length: int) -> None:
        super().__init__(number, n_elements, element_length)
        self._n_cumulative = 1
    
    @staticmethod
    def quantizer():
        return GenericBatchNumber.__quantizer

    def __add__(self, other: BatchNumber):
        result = super().__add__(other)
        result = GenericBatchNumber(
            result._batch,
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
        numbers = (GenericBatchNumber.__quantizer.f2i(f) for f in numbers)
        result = BatchNumber.bind(*numbers, bit_length=bit_length)
        return GenericBatchNumber(result._batch, result._n_elements, result._element_length)


class SignedBatchNumber(BatchNumber):
    __quantizer = SignedQuantizer()

    def __init__(self, batch: int, n_elements: int, element_length: int) -> None:
        super().__init__(batch, n_elements, element_length)
        self.__size = element_length\
            - BatchNumber.PADDING_LENGTH\
            - SignedBatchNumber.PADDING_LENGTH\
            + 1

    @staticmethod
    def quantizer():
        return SignedBatchNumber.__quantizer

    @staticmethod
    def bind(*numbers, bit_length: int):
        signed_numbers = []
        for n in numbers:
            sn = SignedBatchNumber.__quantizer.f2i(n)
            signed_numbers.append(sn.to_int())

        raw_result = BatchNumber.bind(
            *signed_numbers, 
            bit_length=bit_length + SignedInteger.SIGN_SIZE - 1
        )
        result = SignedBatchNumber(
                raw_result._batch,
                raw_result._n_elements,
                raw_result._element_length
            )
        return result

    def get(self, index: int) -> int:
        raw_result = super().get(index)
        signed_number = SignedInteger(
            number=raw_result,
            size_in_bit=self.__size
        )
        return self.__quantizer.i2f(signed_number)

    def __add__(self, other: BatchNumber):
        raw_result = super().__add__(other)
        return SignedBatchNumber(
            batch=raw_result._batch,
            n_elements=raw_result._n_elements,
            element_length=raw_result._element_length
        )
