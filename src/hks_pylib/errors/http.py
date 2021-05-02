from hks_pylib.errors import HKSPylibError


class HTTPError(HKSPylibError):
    "The exception is raised by failures in http module."


class HTTPTypeError(HTTPError):
    "The exception is raised when an invalid http type appears."

