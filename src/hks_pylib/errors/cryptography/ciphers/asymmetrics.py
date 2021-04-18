from hks_pylib.errors.cryptography.ciphers import NotExistKeyError, CipherError


class NotExistPrivateKeyError(NotExistKeyError):
    "Exception is raised when an asymmetric cipher does not find its private key."

class NotExistPublicKeyError(NotExistKeyError):
    "Exception is raised when an asymmetric cipher does not find its public key."


class AsymmetricError(CipherError):
    "Exception is raised by failures in asymmetrics module."


class InvalidEncodingError(AsymmetricError):
    "Exception is raised when saving or loading a file with an invalid encoding."


class DataIsTooLongError(AsymmetricError):
    "Exception is raised by a too long data passed to a cipher."