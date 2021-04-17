class HKSError(Exception):
    "Exception is raised by failures in hks_pylib modules."
    pass


class InvalidParameterError(HKSError):
    "Exception is raised when you pass an invalid parameter to hks methods"


class UnknownHKSError(HKSError):
    "Exception is raised by an unknown error."


class MathError(HKSError):
    "Exception is raised by failures in math module."
    pass


class HTTPError(HKSError):
    "Exception is raised by failures in http module."


class DoneError(HKSError):
    "Exception is raised by failures in done module."


class HKSEnumError(HKSError):
    "Exception is raised by failures in hksenum module."


class CryptographyError(HKSError):
    "Exception is raised by failures in cryptography modules."


class LoggerError(HKSError):
    "Exception is raised by failures in logger module."


class UnknownHTTPTypeError(HTTPError):
    "Exception is raised when you pass unknown http type as a parameter."


class InvalidHTTPKeyFieldError(HTTPError):
    "Exception is raised when you indicate a invalid key."


class ExistedLogConfigElementError(LoggerError):
    "Exception is raised when you add an existed user to config object."


class NotExistedLogConfigElementError(LoggerError):
    "Exception is raised when you access to a not existed user in config object."


class ProtocolError(CryptographyError):
    "Exception is raised by failures in protocol module."

class NotResetProtocolError(ProtocolError):
    "Exception is raised when a protocol must call reset()"

class NotExistKeyError(CryptographyError):
    "Exception is raised when a cipher does not find its key."

class NotExistPrivateKeyError(NotExistKeyError):
    "Exception is raised when an asymmetric cipher does not find its private key."

class NotExistPublicKeyError(NotExistKeyError):
    "Exception is raised when an asymmetric cipher does not find its public key."

class InvalidEncodingError(CryptographyError):
    "Exception is raised when saving or loading a file with an invalid encoding."

class NotResetCipherError(CryptographyError):
    "Exception is raised when you call encrypt() or decrypt() without reset() the cipher."

class DataIsTooLongError(CryptographyError):
    "Exception is raised by a too long data passed to a cipher."

class InvalidCipherParameterError(CryptographyError):
    "Exception is raised when you set an invalid paramter to a cipher."

class NotFinalizeCipherError(CryptographyError):
    "Exception is raised when you has call reset() without calling finalize() yet."

class ExistedCipherIDError(CryptographyError):
    "Exception is raised when a HKSCipher subclass is added twice to CipherID."

class UnAuthenticatedPacketError(CryptographyError):
    "Exception is raised when the HybridCipher digests are not match."

class NotEnoughCipherParameterError(CryptographyError):
    "Exception is raised when you has not yet passed enough paramters to a cipher."

class InvalidBitsLengthError(MathError):
    "Exception is raised when you access invalid range of bits."

class BatchCryptError(CryptographyError):
    "Exception is raised by failures in batchcrypt module."

class InvalidElementError(BatchCryptError):
    "Exception is raised when you access an invalid element in batchnumber."

class NotSetRangeOfQuantizer(BatchCryptError):
    "Exception is raised if you don't provide enough range."

class OutOfRangeQuantizerError(BatchCryptError):
    "Exception is raised when you pass a value out of range in quantizer."

class NotCompileQuatizerError(BatchCryptError):
    "Exception is raised when you quantize without compiling."