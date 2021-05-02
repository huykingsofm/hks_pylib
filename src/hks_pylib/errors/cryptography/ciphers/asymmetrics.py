from hks_pylib.errors.cryptography.ciphers import KeyError, CipherError


class AsymmetricError(CipherError):
    "The exception is raised by failures in asymmetrics module."


class EncodingError(AsymmetricError):
    "The exception is raised when saving or loading a file with an invalid encoding."


class DataIsTooLongError(AsymmetricError):
    "The exception is raised by a too long data passed to a cipher."


class NotExistPrivateKeyError(KeyError, AsymmetricError):
    "The exception is raised when an asymmetric cipher does not find its private key."


class NotExistPublicKeyError(KeyError, AsymmetricError):
    "The exception is raised when an asymmetric cipher does not find its public key."
