from hks_pylib.errors import HKSPylibError


class LoggerError(HKSPylibError):
    "The exception is raised by failures in logger module."


class LogConfigError(LoggerError):
    "The exception is raised by failures related to LogConfig elements."
