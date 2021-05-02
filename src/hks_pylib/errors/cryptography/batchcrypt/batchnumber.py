from hks_pylib.errors.cryptography.batchcrypt import BatchCryptError


class BatchNumberError(BatchCryptError):
    "The exception is raised when you access an invalid element in batchnumber."
