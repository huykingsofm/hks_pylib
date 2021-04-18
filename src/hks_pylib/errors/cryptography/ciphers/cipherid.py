from hks_pylib.errors.cryptography.ciphers import CipherError


class ExistedCipherIDError(CipherError):
    "Exception is raised when a HKSCipher subclass is added twice to CipherID."
