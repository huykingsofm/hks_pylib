from hks_pylib.errors import HKSError


class LoggerError(HKSError):
    "Exception is raised by failures in logger module."


class ExistedLogConfigElementLoggerError(LoggerError):
    "Exception is raised when you add an existed user to config object."


class NotExistedLogConfigElementLoggerError(LoggerError):
    "Exception is raised when you access to a not existed user in config object."
