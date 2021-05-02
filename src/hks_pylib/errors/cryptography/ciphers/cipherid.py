from hks_pylib.errors.cryptography.ciphers import CipherError


class CipherIDError(CipherError):
    "The exception is raised when a HKSCipher subclass is added twice to CipherID."
