import sys
import threading
from typing import Dict, Optional, Set

from hkserror import HTypeError
from hkserror.hkserror import HFormatError
from hks_pylib.errors.logger import LogConfigError
from hks_pylib.logger.standard import Levels, Users

class Output(object):
    def __init__(self) -> None:
        self.__lock = threading.Lock()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def open(self) -> None:
        self.__lock.acquire()

    def close(self) -> None:
        self.__lock.release()

    def write(self, *values, **kwargs) -> None:
        raise NotImplementedError()


class ConsoleOutput(Output):
    def __init__(self) -> None:
        super().__init__()
        self.__is_open = False

    def open(self) -> None:
        self.__is_open = True
        super().open()

    def close(self) -> None:
        super().close()
        self.__is_open = False

    def write(
                self,
                *values: object,
                sep: Optional[str] = " ",
                end: Optional[str] = "\n",
                file = sys.stdout,
                flush: bool = False,
                auto_avoid_conflicting: bool = False
            ) -> None:
        must_closed = False
        if auto_avoid_conflicting and not self.__is_open:
            self.open()
            must_closed = True

        print(*values, sep=sep, end=end, file=file, flush=flush)

        if must_closed:
            self.close()


console_output = ConsoleOutput()

def acprint(*args, **kwargs):
    console_output.write(*args, **kwargs, auto_avoid_conflicting=True)

class FileOutput(Output):
    def __init__(self, filename: str, mode: str = "at") -> None:
        if not isinstance(filename, str):
            raise HTypeError("filename", filename, str)

        if not isinstance(mode, str):
            raise HTypeError("mode", mode, str)

        if mode not in ("at", "wt"):
            raise HFormatError("Parameter mode must be 'at' or 'wt'.")

        super().__init__()
        self.__filename = filename
        self.__mode = mode
        self.__file = None

    def open(self) -> None:
        super().open()
        self.__file = open(self.__filename, self.__mode)

    def close(self) -> None:
        self.__file.close()
        super().close()

    def write(
                self,                
                *values: object,
                sep: Optional[str] = " ",
                end: Optional[str] = "\n",
                flush: bool = False
            ) -> None:
        print(*values, sep=sep, end=end, file=self.__file, flush=flush)


class LogConfig(object):
    def __init__(self) -> None:
        super().__init__()
        self.__user_level: Dict[Users, Set[Levels]] = {}
        self.__user_output: Dict[Users, Output] = {}

    def add_user(self, user: Users):
        if not isinstance(user, Users):
            raise HTypeError("user", user, Users)

        if user in self.__user_level.keys():
            raise LogConfigError("User {} has ready existed in config.".format(user))

        self.__user_level[user] = set()
        self.__user_output[user] = None

    def _add_level_one_element(self, user: Users, level: Levels):
        if not isinstance(user, Users):
            raise HTypeError("user", user, Users)

        if not isinstance(level, Levels):
            raise HTypeError("level", level, Levels)

        if user not in self.__user_level.keys():
            raise LogConfigError("User {} does "
            "not exist.".format(user))

        if level in self.__user_level[user]:
            raise LogConfigError("Level {} has "
            "already existed.".format(level))

        self.__user_level[user].add(level)

    def add_level(self, user: Users, *levels):
        if len(levels) == 0:
            raise HFormatError("Please provide at least one level.")

        for level in levels:
            self._add_level_one_element(user, level)

    def set_output(self, user: Users, output: Output):
        if not isinstance(user, Users):
            raise HTypeError("user", user, Users)

        if not isinstance(output, Output):
            raise HTypeError("output", output, Output)

        if user not in self.__user_level.keys():
            raise LogConfigError("User {} does "
            "not exist.".format(user))

        self.__user_output[user] = output

    def users(self):
        return set(self.__user_level.keys())

    def levels(self, user: Users):
        if not isinstance(user, Users):
            raise HTypeError("user", user, Users)

        if user not in self.__user_level.keys():
            raise LogConfigError("User {} does "
            "not exist.".format(user))

        return self.__user_level[user]

    def output(self, user: str):
        if not isinstance(user, Users):
            raise HTypeError("user", user, Users)

        if user not in self.__user_level.keys():
            raise LogConfigError("User {} does "
            "not exist.".format(user))

        return self.__user_output[user]
