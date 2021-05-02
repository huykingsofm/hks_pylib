import struct

from hkserror import HTypeError
from hkserror.hkserror import HFormatError
from hks_pylib.errors.math import BitwiseError


def ceil_div(a, b):
    return (a + b - 1) // b


def bxor(A: bytes, B: bytes):
    if not isinstance(A, bytes):
        raise HTypeError("A", A, bytes)

    if not isinstance(B, bytes):
        raise HTypeError("B", B, bytes)

    if len(A) != len(B):
        raise HFormatError("Parameter A and B expected to be the same size.")

    iA = int.from_bytes(A, "big")
    iB = int.from_bytes(B, "big")
    iR = iA ^ iB
    
    return iR.to_bytes(len(A), "big")


def float2int(number: float, float_size: int = 4):
    if not isinstance(number, float):
        raise HTypeError("number", number, float)
    
    if not isinstance(float_size, int):
        raise HTypeError("float_size", float_size, int)

    if float_size not in (4, 8):
        raise HFormatError("Parameter float_size only "
        "can be 4 (as float) or 8 (as double).")

    fmt = "!d" if float_size == 8 else "!f"

    packed_number = struct.pack(fmt, number)

    return int.from_bytes(packed_number, "big")


def int2float(number: int, float_size: int = 4):
    if not isinstance(number, int):
        raise HTypeError("number", number, int)
    
    if not isinstance(float_size, int):
        raise HTypeError("float_size", float_size, int)

    if float_size not in (4, 8):
        raise HFormatError("Parameter float_size only "
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
    def __validate(number: int, position: int, length: int, value: int = 0):
        if not isinstance(number, int):
            raise HTypeError("number", number, int)
        
        if not isinstance(position, int):
            raise HTypeError("position", position, int)
        
        if not isinstance(value, int):
            raise HTypeError("value", value, int)
        
        if length is not None and not isinstance(length, int):
            raise HTypeError("length", length, int, None)
        
        if position < 0:
            raise HFormatError("Parameter position and "
            "length expected a non-negative integer.")

        if length is None:
            length = value.bit_length()

        if length <= 0:
            raise HFormatError("Parameter length expected a positive integer.")

        if position - length + 1 < 0:
            raise BitwiseError("You cannot access {} "
            "bits starting from {}-th position.".format(length, position))
    
    @staticmethod
    def max_natural_number(bit_length: int):
        """
        Return the max natural number has the size of bit_length.\n
        Example: `max_natural_number(8) = 255`.
        """

        if not isinstance(bit_length, int):
            raise HTypeError("bit_length", bit_length, int);

        if  bit_length <= 0:
            raise HFormatError("Parameter bit_length expected a positive integer.")

        return ~(1 << bit_length) + (1 << (bit_length + 1))

    @staticmethod
    def turn_on_bits(number: int, position: int, length: int = 1):
        Bitwise.__validate(number, position, length)

        return number | (Bitwise.max_natural_number(length) << (position - length + 1))

    @staticmethod
    def turn_off_bits(number: int, position: int, length: int = 1):
        Bitwise.__validate(number, position, length)

        return number & (~(Bitwise.max_natural_number(length) << (position - length + 1)))

    @staticmethod
    def set_bits(number: int, position: int, value: int, length: int = None):
        """Set `length` bits begining from the `position`
        in the `the number` to the `value`."""        
        Bitwise.__validate(number, position, length, value)
                
        if length is None:
            length = value.bit_length()

        number = Bitwise.turn_off_bits(number, position, length)

        x_shift = value << (position - length + 1)

        return number | x_shift

    @staticmethod
    def get_bits(number: int, position: int, length: int):
        "Get `length` bits beginning from the `position` bit in the `number`."
        Bitwise.__validate(number, position, length)
        
        number = number >> (position - length + 1)
        
        number = number & Bitwise.max_natural_number(length)
        return number
