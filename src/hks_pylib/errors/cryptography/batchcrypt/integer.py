from hks_pylib.errors.cryptography.batchcrypt import BatchCryptError


class IntegerError(BatchCryptError):
    "The exception is raised if adding two different size integer."


class OverflowIntegerError(IntegerError):
    "The exception is raised by detecting a overflow error of integer."
