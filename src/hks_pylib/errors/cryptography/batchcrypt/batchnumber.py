from hks_pylib.errors.cryptography.batchcrypt import BatchCryptError


class InvalidElementBatchNumberError(BatchCryptError):
    "Exception is raised when you access an invalid element in batchnumber."

class MismatchedTypeBatchNumberError(BatchCryptError):
    "Exception is raised when you perform an operation on two different type of batchnumber."