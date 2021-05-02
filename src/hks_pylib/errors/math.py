from hks_pylib.errors import HKSPylibError

class MathError(HKSPylibError):
    "The exception is raised by failures in math module."
    pass

class BitwiseError(MathError):
    "The exception is raised by failures in Bitwise operation."
