class HKSError(Exception):
    "Exception is raised by failures in hks_pylib modules."
    pass


class InvalidParameterError(HKSError):
    "Exception is raised when you pass an invalid parameter to hks methods"


class UnknownHKSError(HKSError):
    "Exception is raised by an unknown error."
