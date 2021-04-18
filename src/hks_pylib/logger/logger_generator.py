from typing import Type

from hks_pylib.logger.logger import BaseLogger
from hks_pylib.logger.config import LogConfig, console_output, FileOutput

from hks_pylib.errors import InvalidParameterError

class LoggerGenerator(object):
    def __init__(self, logger_cls: Type[BaseLogger], **kwargs) -> None:
        if not issubclass(logger_cls, BaseLogger):
            raise InvalidParameterError("Parameter logger_cls must be a subclass of BaseLogger.")

        super().__init__()
        self._logger_cls = logger_cls
        self._logger_kwargs = kwargs

    def generate(self, name, display):
        return self._logger_cls(name=name, display=display, **self._logger_kwargs)


class StandardLoggerGenerator(LoggerGenerator):
    def __init__(self, log_file_name: str) -> None:
        if not isinstance(log_file_name, str):
            raise InvalidParameterError("Parameter log_file_name must be a str.")

        self._config = LogConfig()
        
        self._config.add_user("user")
        self._config.add_level("user", "info", "warning")
        self._config.set_output("user", console_output)
        
        self._config.add_user("dev")
        self._config.add_level(
            "dev",
            "info", "warning", "error",
            "debug", "critical", "benchmark"
        )
        self._config.set_output("dev", FileOutput(log_file_name))

        super().__init__(BaseLogger, config=self._config)
