import datetime

from typing import Dict, Iterable

from hkserror.hkserror import HTypeError

from hks_pylib.hksenum import HKSEnum
from hks_pylib.logger.config import LogConfig, console_output, FileOutput

from hks_pylib.errors.logger import LoggerError
from hks_pylib.logger.standard import Levels, StdLevels, StdUsers, Users


class Display(HKSEnum):
    ALL = "all"


class BaseLogger(object):
    def __init__(self, name: str, config: LogConfig, display: Dict[Users, Levels]):
        if name is not None and not isinstance(name, str):
            raise HTypeError("name", name, str, None)

        if not isinstance(config, LogConfig):
            raise HTypeError("config", config, LogConfig)

        if display is not Display.ALL and not isinstance(display, dict):
            raise HTypeError("display", display, dict)

        self._name = name
        self._config = config
        self._display = display

        for user in self._display:
            if user not in self._config.users():
                raise LoggerError(f"Displayed user "
                f"must be in {self._config.users()}, rather than {user}.")

            if self._display[user] is not Display.ALL\
                and not isinstance(self._display[user], Iterable):
                raise HTypeError("display of {}".format(user), 
                self._display[user], Iterable, Display.ALL)

            if self._display[user] is Display.ALL:
                continue

            for level in self._display[user]:
                if level not in self._config.levels(user):
                    raise LoggerError(f"Displayed "
                    f"level of '{user}' must be in the "
                    f"{self._config.levels(user)}, rather than {level}.")

    def __call__(self, user: Users, level: Levels, *values, **kwargs):
        if not isinstance(user, Users):
            raise HTypeError("user", user, Users)

        if not isinstance(level, Levels):
            raise HTypeError("level", level, Levels)

        if user not in self._config.users():
            raise LoggerError(f"User must be in "
            f"{list(self._config.users())}, rather than {user}.")

        if level not in self._config.levels(user):
            raise LoggerError(f"Level of '{user}' "
            f"must be in {self._config.levels(user)}, rather than {level}.")

        if user not in self._display:
            return

        if self._display[user] is not Display.ALL and level not in self._display[user]:
            return

        output = self._config.output(user)
        output.open()

        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if self._name:
            output.write(f"{now} {level.name.upper()} [{self._name}] -", *values, **kwargs)
        else:
            output.write(f"{now} {level.name.upper()} -", *values, **kwargs)

        output.close()

    def use_dict(self, print_dict: dict):
        if not isinstance(print_dict, dict):
            raise HTypeError("print_dict", dict)

        for user in print_dict.keys():
            for level in print_dict[user]:
                self.__call__(user, level, print_dict[user][level])


class StandardLogger(BaseLogger):
    def __init__(self, name: str, log_file_name: str, display: dict):
        if not isinstance(log_file_name, str):
            raise HTypeError("log_file_name", log_file_name, str)

        config = LogConfig()

        config.add_user(StdUsers.USER)
        config.add_level(StdUsers.USER, StdLevels.INFO, StdLevels.WARNING)
        config.set_output(StdUsers.USER, console_output)

        config.add_user(StdUsers.DEV)
        config.add_level(StdUsers.DEV, StdLevels.INFO, StdLevels.WARNING)
        config.add_level(StdUsers.DEV, StdLevels.ERROR, StdLevels.DEBUG)
        config.add_level(StdUsers.DEV, StdLevels.CRITICAL, StdLevels.BENCHMARK)
        config.set_output(StdUsers.DEV, FileOutput(log_file_name))

        super().__init__(name, config, display)


class InvisibleLogger(BaseLogger):
    def __init__(self):
        config = LogConfig()
        super().__init__(None, config, {})
