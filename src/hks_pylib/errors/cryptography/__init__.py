from hks_pylib.errors import HKSPylibError


class CryptographyError(HKSPylibError):
    "The exception is raised by failures in cryptography modules."


class ResetError(CryptographyError):
    "The exception is raised when a cipher/protocol/hashes uses without reset."