from hks_pylib.errors.cryptography import CryptographyError


class ProtocolError(CryptographyError):
    "Exception is raised by failures in protocol module."


class NotResetProtocolError(ProtocolError):
    "Exception is raised when a protocol must call reset()"
