from hks_pylib.math import Bitwise

from hks_pylib.errors import InvalidParameterError
from hks_pylib.errors.cryptography.batchcrypt.integer import OverflowIntegerError
from hks_pylib.errors.cryptography.batchcrypt.integer import OutOfRangeIntegerError
from hks_pylib.errors.cryptography.batchcrypt.integer import MismatchedSizeIntegerError

class SignedInteger(object):
    SIGN_SIZE = 2

    @staticmethod
    def is_overflow(number: int, size_in_bit: int):
        total_size = size_in_bit + SignedInteger.SIGN_SIZE - 1
        value_size = size_in_bit - 1
        value = Bitwise.get_bits(
            number=number,
            position=value_size - 1,
            length=value_size
        )

        sign = Bitwise.get_bits(
            number=number,
            position=total_size - 1,
            length=SignedInteger.SIGN_SIZE
        )

        if sign != 0 and sign != 3:
            return True

        if sign == 3 and value == 0:
            return True
        
        return False

    @staticmethod
    def is_out_of_range(number: int, size_int_bit: int):
        max_value = Bitwise.get_max_number(size_int_bit - 1)
        if number < -max_value or number > max_value:
            return True
        
        return False

    @staticmethod
    def from_int(number: int, size_in_bit: int):
        total_size = size_in_bit + SignedInteger.SIGN_SIZE - 1
        value_size = size_in_bit - 1

        if SignedInteger.is_out_of_range(number, size_in_bit):
            raise OutOfRangeIntegerError("Imported number is out "
            "of range (signed integer {}-bit)".format(size_in_bit))

        actual_number = Bitwise.get_bits(
            number=number,
            position=value_size - 1,
            length=value_size
        )
        
        raw_number = Bitwise.set_bits(
            number=0,
            position=value_size - 1,
            value=actual_number,
            length=value_size
        )
        raw_number = Bitwise.set_bits(
            number=raw_number,
            position=total_size - 1,
            value=3 if number < 0 else 0,  # positive (00), negative (11)
            length=SignedInteger.SIGN_SIZE
        )

        return SignedInteger(raw_number, size_in_bit)

    def __init__(self, number: int, size_in_bit: int) -> None:
        super().__init__()
        self._total_size = size_in_bit + self.SIGN_SIZE - 1
        self._value_size = size_in_bit - 1

        if self.is_overflow(number, size_in_bit):
            raise OverflowIntegerError("Invalid sign value, "
            "expected 0 (positive) or 3 (negative).")

        self._number = Bitwise.get_bits(
            number=number,
            position=self._total_size - 1,
            length=self._total_size
        )

    def to_int(self):
        return self._number

    def total_size(self):
        return self._total_size

    def value(self):
        sign = Bitwise.get_bits(
            number=self._number,
            position=self._total_size - 1,
            length=self.SIGN_SIZE
        )

        value = Bitwise.get_bits(
            number=self._number,
            position=self._value_size - 1,
            length=self._value_size
        )

        if sign == 3:
            value = -Bitwise.get_bits(
                number=~value+1,
                position=self._value_size - 1,
                length=self._value_size
            )

        return value

    def __ops__(self, other, operator):
        if not isinstance(other, SignedInteger):
            raise InvalidParameterError("Parameter of "
            "additive operator must be SignedInteger objects.")

        if self._total_size != other._total_size:
            raise MismatchedSizeIntegerError("Two operands must be "
            "the same size ({} != {}).".format(self._total_size, other._total_size))

        raw_result = operator(self._number, other._number)

        return SignedInteger(raw_result, self._value_size + 1)

    def __add__(self, other):
        add = lambda x, y: x + y
        return self.__ops__(other, add)

    def __sub__(self, other):
        sub = lambda x, y: x - y
        return self.__ops__(other, sub)
    
    def __mul__(self, other):
        mul = lambda x, y: x * y
        return self.__ops__(other, mul)

    def __cmp__(self, other, operator):
        if isinstance(other, SignedInteger):
            return operator(self.value(), other.value())
        else:
            return operator(self.value(), other)

    def __lt__(self, other):
        lt = lambda x, y: x < y
        return self.__cmp__(other, lt)
    
    def __le__(self, other):
        le = lambda x, y: x <= y
        return self.__cmp__(other, le)
        
    def __gt__(self, other):
        gt = lambda x, y: x > y
        return self.__cmp__(other, gt)
        
    def __ge__(self, other):
        ge = lambda x, y: x >= y
        return self.__cmp__(other, ge)
        
    def __eq__(self, other):
        eq = lambda x, y: x == y
        return self.__cmp__(other, eq)
        
    def __ne__(self, other):
        ne = lambda x, y: x != y
        return self.__cmp__(other, ne)
