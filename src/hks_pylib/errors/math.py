from hks_pylib.errors import HKSError

class MathError(HKSError):
    "Exception is raised by failures in math module."
    pass


class InvalidBitsLengthMathError(MathError):
    "Exception is raised when you access invalid range of bits."
