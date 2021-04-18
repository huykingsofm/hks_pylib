from hks_pylib.errors.cryptography.batchcrypt import BatchCryptError


class OutOfRangeIntegerError(BatchCryptError):
    "Exception is raised when you pass out of range integer."

class MismatchedSizeIntegerError(BatchCryptError):
    "Exception is raised if adding two different size integer."

class OverflowIntegerError(BatchCryptError):
    "Exception is raised by detecting a overflow error of integer."