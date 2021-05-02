from hks_pylib.errors.cryptography.batchcrypt import BatchCryptError


class QuantizerError(BatchCryptError):
    "The exception is raised when you quantize without compiling."


class RangeOfQuantizerError(QuantizerError):
    "The exception is raised if you don't provide enough range."


class OverflowQuantizerError(QuantizerError):
    "The exception is raised when you pass a value out of range in quantizer."
