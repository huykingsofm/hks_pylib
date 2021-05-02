from hks_pylib.errors.cryptography.ciphers import CipherError


class SymmetricError(CipherError):
    "The exception is raised by failures in SymmetricCipher"


class UnAuthenticatedPacketError(SymmetricError):
    "The exception is raised when the HybridCipher digests are not match."
