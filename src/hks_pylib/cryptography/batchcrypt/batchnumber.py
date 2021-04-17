from hks_pylib.math import Bitwise
from hks_pylib.errors import InvalidElementError


class BatchNumber(object):
    "A placeholder class"
    pass


class BatchNumber(object):
    PADDING_LENGTH = 2

    def __init__(
                self,
                number: int,
                n_elements: int,
                element_length: int
            ) -> None:
        self._n_elements = n_elements
        self._element_length = element_length

        self._number = number
        self._number_length = self._n_elements * self._element_length

    def get(self, index: int) -> int:
        if not isinstance(index, int):
            raise InvalidElementError("Parameter i_element must be a int.")

        if index >= self._n_elements or index < 0:
            raise InvalidElementError("You can only access elements "
            "starting from 0 to {}".format(self._n_elements - 1))

        return Bitwise.get_bits(
            number=self._number,
            position=self._number_length\
                - index * self._element_length - 1,
            length=self._element_length
        )

    def __getitem__(self, index: int):
        return self.get(index)


    def __add__(self, other: BatchNumber):
        assert self._n_elements == other._n_elements
        assert self._element_length == other._element_length

        return BatchNumber(
            self._number + other._number,
            self._n_elements,
            self._element_length
        )

    
    def __iadd__(self, other: BatchNumber):
        assert self._n_elements == other._n_elements
        assert self._element_length == other._element_length

        self._number += other._number

    def __str__(self) -> str:
        return bin(self._number)

    def __repr__(self) -> str:
        return str(self)
    
    def toint(self) -> int:
        return self._number

    @staticmethod
    def bind(*numbers, bit_length: int = 8):
        element_length = bit_length + BatchNumber.PADDING_LENGTH

        batch_length = element_length * len(numbers)
        batch_number = 0

        for i, number in enumerate(numbers):
            batch_number = Bitwise.set_bits(
                number=batch_number,
                position=batch_length - element_length * i\
                    - BatchNumber.PADDING_LENGTH - 1,
                length=bit_length,
                value=number
            )

        return BatchNumber(batch_number, len(numbers), element_length)
