from hks_pylib.errors.cryptography.batchcrypt import BatchCryptError


class NotSetRangeOfQuantizerError(BatchCryptError):
    "Exception is raised if you don't provide enough range."


class OverflowQuantizerError(BatchCryptError):
    "Exception is raised when you pass a value out of range in quantizer."


class NotCompileQuatizerError(BatchCryptError):
    "Exception is raised when you quantize without compiling."