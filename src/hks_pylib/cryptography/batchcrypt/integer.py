from hks_pylib.math import Bitwise

from hks_pylib.errors import InvalidParameterError
from hks_pylib.errors.cryptography.batchcrypt.integer import OverflowIntegerError
from hks_pylib.errors.cryptography.batchcrypt.integer import OutOfRangeIntegerError
from hks_pylib.errors.cryptography.batchcrypt.integer import MismatchedSizeIntegerError

class SignedInteger(object):
    __SIGN_SIZE = 2

    def sign_size():
        return SignedInteger.__SIGN_SIZE

    def set_sign_size(value: int):
        if not isinstance(value, int) or value < 1:
            raise InvalidParameterError("Sign size must be a "
            "int larger than 0.")

        SignedInteger.__SIGN_SIZE = value

    @staticmethod
    def is_overflow(number: int, size: int):
        value_size = size - SignedInteger.sign_size()
        value = Bitwise.get_bits(
                number=number,
                position=value_size - 1,
                length=value_size
            )

        sign = Bitwise.get_bits(
                number=number,
                position=size - 1,
                length=SignedInteger.sign_size()
            )

        if sign != 0 and sign != Bitwise.max_natural_number(SignedInteger.sign_size()):
            return True

        if sign == Bitwise.max_natural_number(SignedInteger.sign_size()) and value == 0:
            return True
        
        return False

    @staticmethod
    def is_out_of_range(number: int, size: int):
        max_value = Bitwise.max_natural_number(size - SignedInteger.sign_size())
        if number < -max_value or number > max_value:
            return True
        
        return False

    @staticmethod
    def from_int(number: int, size: int):
        value_size = size - SignedInteger.sign_size()

        if SignedInteger.is_out_of_range(number, size):
            raise OutOfRangeIntegerError("Imported number is out "
            "of range (signed integer {}-bit)".format(size))

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
            sign_value = Bitwise.max_natural_number(SignedInteger.sign_size()) 
        else:
            sign_value = 0

        raw_number = Bitwise.set_bits(
                number=raw_number,
                position=size - 1,
                value=sign_value,
                length=SignedInteger.sign_size()
            )

        return SignedInteger(raw_number, size)

    def __init__(self, number: int, size: int) -> None:
        super().__init__()
        self._size = size
        self._value_size = size - SignedInteger.sign_size()

        if self.is_overflow(number, size):
            max_value = Bitwise.max_natural_number(self.value_size())
            min_value = -max_value
            raise OverflowIntegerError("Invalid number, "
            "expected {} <= number <= {}, rather than {}.".format(
                min_value, max_value, number)
            )

        self._raw_number = Bitwise.get_bits(
                number=number,
                position=self.size() - 1,
                length=self.size()
            )

    def raw(self):
        return self._raw_number

    def size(self):
        return self._size

    def value_size(self):
        return self._value_size

    def value(self):
        sign = Bitwise.get_bits(
                number=self.raw(),
                position=self.size() - 1,
                length=SignedInteger.sign_size()
            )

        value = Bitwise.get_bits(
                number=self.raw(),
                position=self.value_size() - 1,
                length=self.value_size()
            )

        if sign == Bitwise.max_natural_number(SignedInteger.sign_size()):
            value = 0 - Bitwise.get_bits(
                    number=~value+1,
                    position=self.value_size() - 1,
                    length=self.value_size()
                )

        return value

    def __ops__(self, other, operator):
        if not isinstance(other, type(self)):
            raise InvalidParameterError("Parameter of "
            "arithmetic operator must be {} objects.".format(type(self).__name__))

        if self.size() != other.size():
            raise MismatchedSizeIntegerError("Two operands must be "
            "the same size ({} != {}).".format(self.size(), other.size()))

        raw_result = operator(self.raw(), other.raw())

        return SignedInteger(raw_result, self.size())

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
        if isinstance(other, type(self)):
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
