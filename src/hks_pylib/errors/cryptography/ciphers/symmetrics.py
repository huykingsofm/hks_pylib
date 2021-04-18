from hks_pylib.errors.cryptography.ciphers import CipherError


class UnAuthenticatedPacketError(CipherError):
    "Exception is raised when the HybridCipher digests are not match."