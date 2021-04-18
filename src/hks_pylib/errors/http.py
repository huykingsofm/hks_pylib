from hks_pylib.errors import HKSError


class HTTPError(HKSError):
    "Exception is raised by failures in http module."


class UnknownHTTPTypeError(HTTPError):
    "Exception is raised when you pass unknown http type as a parameter."


class InvalidHTTPKeyFieldError(HTTPError):
    "Exception is raised when you indicate a invalid key."
