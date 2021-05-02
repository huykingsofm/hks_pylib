from hks_pylib.errors.cryptography import CryptographyError


class CipherError(CryptographyError):
    "The exception is raised by failures in ciphers modules."


class KeyError(CipherError):
    "The exception is raised when a cipher does not find its key."


class CipherParameterError(CipherError):
    "The exception is raised when you set an invalid paramter to a cipher."


class FinalizeCipherError(CipherError):
    "The exception is raised when you has call reset() without calling finalize() yet."
