import datetime

from typing import Iterable
from hks_pylib.errors import InvalidParameterError, NotExistedLogConfigElementError

from hks_pylib.hksenum import HKSEnum
from hks_pylib.logger.config import LogConfig, console_output, FileOutput


class Display(HKSEnum):
    ALL = 0


class BaseLogger(object):
    def __init__(self, name: object, config: LogConfig, display: dict):
        if not isinstance(config, LogConfig):
            raise InvalidParameterError("Parameter config must be a LogConfig object.")
        
        if not isinstance(display, dict):
            raise InvalidParameterError("Parameter display must be a dict.")

        self.__name = name
        self._config = config
        self._display = display

        for user in self._display:
            if user not in self._config.users():
                raise NotExistedLogConfigElementError(f"Displayed user must be in "
                    f"{self._config.users()}, rather than {user}.")
            
            if self._display[user] is not Display.ALL\
                and not isinstance(self._display[user], Iterable):
                raise InvalidParameterError("Parameter display of user {} "
                "must be a iterable or Display.ALL.".format(user))

            if self._display[user] is Display.ALL:
                continue

            for level in self._display[user]:
                if level not in self._config.level(user):
                    raise NotExistedLogConfigElementError(f"Displayed level of '{user}' "
                    f"must be in the {self._config.level(user)}, rather than {level}.")

    def __call__(self, user, level, *values, **kwargs):
        if user not in self._config.users():
            raise NotExistedLogConfigElementError(f"User must be in "
            f"{list(self._config.users())}, rather than {user}.")

        if level not in self._config.level(user):
            raise NotExistedLogConfigElementError(f"Level of '{user}' must be in "
            f"{self._config.level(user)}, rather than {level}.")

        if user not in self._display:
            return

        if self._display[user] is not Display.ALL and level not in self._display[user]:
            return

        output = self._config.output(user)
        output.open()

        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if self.__name:
            output.write(f"{now} {level.upper()} [{self.__name}] -", *values, **kwargs)
        else:
            output.write(f"{now} {level.upper()} -", *values, **kwargs)

        output.close()

    def use_dict(self, print_dict: dict):
        if not isinstance(print_dict, dict):
            raise InvalidParameterError("Parameter print_dict must be a dict.")

        for user in print_dict.keys():
            for level in print_dict[user]:
                self.__call__(user, level, print_dict[user][level])


class StandardLogger(BaseLogger):
    def __init__(self, name: str, log_file_name: str, display: dict):
        config = LogConfig()
        
        config.add_user("user")
        config.add_level("user", "info", "warning")
        config.add_level("user", console_output)

        config.add_user("dev")
        config.add_level("dev", "info", "warning", "error", "debug", "critical", "benchmark")
        config.set_output("dev", FileOutput(log_file_name))

        super().__init__(name, config, display)
