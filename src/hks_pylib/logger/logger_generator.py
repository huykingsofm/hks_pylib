from typing import Type

from hks_pylib.logger.standard import StdLevels, StdUsers
from hks_pylib.logger.logger import BaseLogger, InvisibleLogger
from hks_pylib.logger.config import LogConfig, console_output, FileOutput

from hkserror.hkserror import HTypeError


class LoggerGenerator(object):
    def __init__(self, logger_cls: Type[BaseLogger], **kwargs) -> None:
        if not issubclass(logger_cls, BaseLogger):
            raise HTypeError("logger_cls", logger_cls, Type[BaseLogger])

        super().__init__()
        self._logger_cls = logger_cls
        self._logger_kwargs = kwargs

    def generate(self, name: str, display: dict):
        return self._logger_cls(name=name, display=display, **self._logger_kwargs)


class StandardLoggerGenerator(LoggerGenerator):
    def __init__(self, log_file_name: str) -> None:
        if not isinstance(log_file_name, str):
            raise HTypeError("log_file_name", log_file_name, str)

        self._config = LogConfig()

        self._config.add_user(StdUsers.USER)
        self._config.add_level(StdUsers.USER, StdLevels.INFO, StdLevels.WARNING)
        self._config.set_output(StdUsers.USER, console_output)

        self._config.add_user(StdUsers.DEV)
        self._config.add_level(StdUsers.DEV, StdLevels.INFO, StdLevels.WARNING)
        self._config.add_level(StdUsers.DEV, StdLevels.ERROR, StdLevels.DEBUG)
        self._config.add_level(StdUsers.DEV, StdLevels.CRITICAL, StdLevels.BENCHMARK)
        self._config.set_output(StdUsers.DEV, FileOutput(log_file_name))

        super().__init__(BaseLogger, config=self._config)


class InvisibleLoggerGenerator(LoggerGenerator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(logger_cls=InvisibleLogger)

    def generate(self, name, display):
        return super().generate(name, display)
