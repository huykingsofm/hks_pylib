import struct

from hks_pylib.errors import InvalidParameterError
from hks_pylib.errors.math import InvalidBitsLengthMathError


def ceil_div(a, b):
    return (a + b - 1) // b


def bxor(A: bytes, B: bytes):
    if not isinstance(A, bytes) or not isinstance(B, bytes):
        raise InvalidParameterError("Parameter A and B must be bytes objects.")

    if len(A) != len(B):
        raise InvalidParameterError("Parameter A and B must be the same size.")

    iA = int.from_bytes(A, "big")
    iB = int.from_bytes(B, "big")
    iR = iA ^ iB
    
    return iR.to_bytes(len(A), "big")


def float2int(number: float, float_size: int = 4):
    if float_size not in (4, 8):
        raise InvalidParameterError("Number size only "
        "can be 4 (as float) or 8 (as double).")

    fmt = "!d" if float_size == 8 else "!f"

    packed_number = struct.pack(fmt, number)

    return int.from_bytes(packed_number, "big")


def int2float(number: int, float_size: int = 4):
    if float_size not in (4, 8):
        raise InvalidParameterError("Number size only "
        "can be 4 (as float) or 8 (as double).")

    fmt = "!d" if float_size == 8 else "!f"
    packed_number = number.to_bytes(float_size, "big")
    return struct.unpack(fmt, packed_number)[0]


class Bitwise(object):
    """
    Bitwise
    ===========
    A static class of bitwise operators.

    --------------------

    Important 1. The order of bits starts from 0 and is numbered from right to left.  
    ---------
    Example of `10` (decimal) -> `1010` (binary):  
    `Ord: 7 6 5 4 3 2 1 0`
    `Bin: 0 0 0 0 1 0 1 0`

    Important 2. The operators which get some bits from i-th bit will get from left to right. 
    ----------
    Example of get 4 bits from 5th bit of `123` (decimal) -> `01111011` (binary):
    `Ord: 7 6 5 4 3 2 1 0`
    `Bin: 0 1 1 1 1 0 1 1`
    `Out: 0 0 0 0 1 1 1 0`
    """
    
    
    @staticmethod
    def max_natural_number(bit_length: int):
        """
        Return the max natural number has the size of bit_length.\n
        Example: `max_natural_number(8) = 255`.
        """

        if not isinstance(bit_length, int) or bit_length <= 0:
            raise InvalidParameterError("Parameter bit_length "
            "must be an int and larger than 0");

        return ~(1 << bit_length) + (1 << (bit_length + 1))

    @staticmethod
    def turn_on_bits(number: int, position: int, length: int = 1):
        if not isinstance(number, int)\
            or not isinstance(position, int)\
            or not isinstance(length, int):
            raise InvalidParameterError("Paramters must be int.")
        
        if position < 0 or length <=0:
            raise InvalidParameterError("Expect position >= 0 and length > 0.")

        if position - length + 1 < 0:
            raise InvalidBitsLengthMathError("You cannot access {} "
            "bits starting from {}-th position.".format(length, position))

        return number | (Bitwise.max_natural_number(length) << (position - length + 1))

    @staticmethod
    def turn_off_bits(number: int, position: int, length: int = 1):
        if not isinstance(number, int)\
            or not isinstance(position, int)\
            or not isinstance(length, int):
            raise InvalidParameterError("Paramters must be int.")
        
        if position < 0 or length <=0:
            raise InvalidParameterError("Expect position >= 0 and length > 0.")
        
        if position - length + 1 < 0:
            raise InvalidBitsLengthMathError("You cannot access {} "
            "bits starting from {}-th position.".format(length, position))

        return number & (~(Bitwise.max_natural_number(length) << (position - length + 1)))

    @staticmethod
    def set_bits(number: int, position: int, value: int, length: int = None):
        """Set `length` bits begining from the `position`
        in the `the number` to the `value`."""        

        if not isinstance(number, int)\
            or not isinstance(position, int)\
            or not isinstance(value, int)\
            or (length is not None and not isinstance(length, int)):
            raise InvalidParameterError("Paramters must be int.")
        
        if position < 0 or length <=0:
            raise InvalidParameterError("Expect position >= 0 and length > 0.")
        
        if length is None:
            length = value.bit_length()

        if position - length + 1 < 0:
            raise InvalidBitsLengthMathError("You cannot access {} "
            "bits starting from {}-th position.".format(length, position))

        number = Bitwise.turn_off_bits(number, position, length)

        x_shift = value << (position - length + 1)

        return number | x_shift

    @staticmethod
    def get_bits(number: int, position: int, length: int):
        "Get `length` bits beginning from the `position` bit in the `number`."

        if not isinstance(number, int)\
            or not isinstance(position, int)\
            or not isinstance(length, int):
            raise InvalidParameterError("Paramters must be int.")
        
        if position < 0 or length <=0:
            raise InvalidParameterError("Expect position >= 0 and length > 0.")
        
        if position - length + 1 < 0:
            raise InvalidBitsLengthMathError("You cannot access {} "
            "bits starting from {}-th position.".format(length, position))
        
        number = number >> (position - length + 1)
        
        number = number & Bitwise.max_natural_number(length)
        return number
