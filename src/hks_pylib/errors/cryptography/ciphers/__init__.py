from hks_pylib.errors.cryptography import CryptographyError


class CipherError(CryptographyError):
    "Exception is raised by failures in ciphers modules."


class NotExistKeyError(CipherError):
    "Exception is raised when a cipher does not find its key."


class NotResetCipherError(CipherError):
    "Exception is raised when you call encrypt() or decrypt() without reset() the cipher."


class InvalidCipherParameterError(CipherError):
    "Exception is raised when you set an invalid paramter to a cipher."


class NotFinalizeCipherError(CipherError):
    "Exception is raised when you has call reset() without calling finalize() yet."


class NotEnoughCipherParameterError(CipherError):
    "Exception is raised when you has not yet passed enough paramters to a cipher."
