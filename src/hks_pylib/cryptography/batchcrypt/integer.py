from hks_pylib.math import Bitwise

from hks_pylib.errors import InvalidParameterError
from hks_pylib.errors.cryptography.batchcrypt.integer import OverflowIntegerError
from hks_pylib.errors.cryptography.batchcrypt.integer import OutOfRangeIntegerError
from hks_pylib.errors.cryptography.batchcrypt.integer import MismatchedSizeIntegerError

class SignedInteger(object):
    __SIGN_SIZE = 4

    @staticmethod
    def sign_size():
        return SignedInteger.__SIGN_SIZE

    @staticmethod
    def total_size_(original_size: int):
        return original_size + SignedInteger.sign_size() - 1

    @staticmethod
    def is_overflow(number: int, original_size: int):
        total_size = original_size + SignedInteger.sign_size() - 1
        value_size = original_size - 1
        value = Bitwise.get_bits(
                number=number,
                position=value_size - 1,
                length=value_size
            )

        sign = Bitwise.get_bits(
                number=number,
                position=total_size - 1,
                length=SignedInteger.sign_size()
            )

        if sign != 0 and sign != Bitwise.get_max_number(SignedInteger.sign_size()):
            return True

        if sign == Bitwise.get_max_number(SignedInteger.sign_size()) and value == 0:
            return True
        
        return False

    @staticmethod
    def is_out_of_range(number: int, original_size: int):
        max_value = Bitwise.get_max_number(original_size - 1)
        if number < -max_value or number > max_value:
            return True
        
        return False

    @staticmethod
    def from_int(number: int, original_size: int):
        total_size = original_size + SignedInteger.sign_size() - 1
        value_size = original_size - 1

        if SignedInteger.is_out_of_range(number, original_size):
            raise OutOfRangeIntegerError("Imported number is out "
            "of range (signed integer {}-bit)".format(original_size))

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
        
        if number < 0: # positive (0..0), negative (1..1)
            sign_value = Bitwise.get_max_number(SignedInteger.sign_size()) 
        else:
            sign_value = 0

        raw_number = Bitwise.set_bits(
                number=raw_number,
                position=total_size - 1,
                value=sign_value,
                length=SignedInteger.sign_size()
            )

        return SignedInteger(raw_number, original_size)

    def __init__(self, number: int, original_size: int) -> None:
        super().__init__()
        self._total_size = original_size + self.sign_size() - 1
        self._value_size = original_size - 1

        if self.is_overflow(number, original_size):
            raise OverflowIntegerError("Invalid sign value, "
            "expected 0 (positive) or {} (negative).".format(
                Bitwise.get_max_number(SignedInteger.sign_size()))
            )

        self._number = Bitwise.get_bits(
                number=number,
                position=self._total_size - 1,
                length=self._total_size
            )

    def to_int(self):
        return self._number

    def total_size(self):
        return self._total_size

    def original_size(self):
        return self._value_size + 1

    def value(self):
        sign = Bitwise.get_bits(
                number=self._number,
                position=self._total_size - 1,
                length=self.sign_size()
            )

        value = Bitwise.get_bits(
                number=self._number,
                position=self._value_size - 1,
                length=self._value_size
            )

        if sign == Bitwise.get_max_number(SignedInteger.sign_size()):
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

        return SignedInteger(raw_result, self.original_size())

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
