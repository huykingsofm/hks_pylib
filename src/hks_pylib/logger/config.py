import sys
import threading
from typing import Dict, Optional, Set

from hks_pylib.errors import InvalidParameterError
from hks_pylib.errors import ExistedLogConfigElementError
from hks_pylib.errors import NotExistedLogConfigElementError

class Output(object):
    def __init__(self) -> None:
        self.__lock = threading.Lock()

    def open(self) -> None:
        self.__lock.acquire()

    def close(self) -> None:
        self.__lock.release()

    def write(self, *values, **kwargs) -> None:
        raise NotImplementedError()


class ConsoleOutput(Output):
    def write(
                self,
                *values: object,
                sep: Optional[str] = " ",
                end: Optional[str] = "\n",
                file = sys.stdout,
                flush: bool = False,
                auto_avoid_conflict: bool = False
            ) -> None:
        if auto_avoid_conflict:
            self.open()

        print(*values, sep=sep, end=end, file=file, flush=flush)

        if auto_avoid_conflict:
            self.close()

console_output = ConsoleOutput()


class FileOutput(Output):
    def __init__(self, filename: str, mode: str = "at") -> None:
        if not isinstance(filename, str):
            raise InvalidParameterError("Parameter filename must be a str.")

        if not isinstance(mode, str):
            raise InvalidParameterError("Parameter mode must be a str.")

        super().__init__()
        self.__file = filename
        self.__mode = "at"
        self.__stream = None

    def open(self) -> None:
        super().open()
        self.__stream = open(self.__file, self.__mode)

    def close(self) -> None:
        self.__stream.close()
        super().close()

    def write(
                self,                
                *values: object,
                sep: Optional[str] = " ",
                end: Optional[str] = "\n",
                flush: bool = False
            ) -> None:
        print(*values, sep=sep, end=end, file=self.__stream, flush=flush)


class LogConfig(object):
    def __init__(self) -> None:
        super().__init__()
        self.__user_level: Dict[str, Set[str]] = {}
        self.__user_output: Dict[str, Output] = {}

    def add_user(self, user: str):
        if not isinstance(user, str):
            raise InvalidParameterError("Parameter user must be a str.")

        assert user not in self.__user_level.keys()

        self.__user_level[user] = set()
        self.__user_output[user] = None

    def _add_level_one_element(self, user: str, level: str):
        if not isinstance(user, str):
            raise InvalidParameterError("Parameter user must be a str.")

        if not isinstance(level, str):
            raise InvalidParameterError("Parameter level must be a str.")

        if user not in self.__user_level.keys():
            raise NotExistedLogConfigElementError("User {} does not exist.".format(user))

        if level in self.__user_level[user]:
            raise ExistedLogConfigElementError("Level {} has already existed.".format(level))

        self.__user_level[user].add(level)

    def add_level(self, user: str, *levels):
        if len(levels) == 0:
            raise InvalidParameterError("Please provide at least one level.")

        for level in levels:
            self._add_level_one_element(user, level)

    def set_output(self, user: str, output: Output):
        if not isinstance(user, str):
            raise InvalidParameterError("Paramter user must be a str.")

        if not isinstance(output, Output):
            raise InvalidParameterError("Paramter output must be an Output object.")
        
        if user not in self.__user_level.keys():
            raise NotExistedLogConfigElementError("User {} does not exist.".format(user))
        
        self.__user_output[user] = output

    def users(self):
        return set(self.__user_level.keys())

    def level(self, user: str):
        if not isinstance(user, str):
            raise InvalidParameterError("Paramter user must be a str.")

        if user not in self.__user_level.keys():
            raise NotExistedLogConfigElementError("User {} does not exist.".format(user))

        return self.__user_level[user]

    def output(self, user: str):
        if not isinstance(user, str):
            raise InvalidParameterError("Paramter user must be a str.")

        if user not in self.__user_level.keys():
            raise NotExistedLogConfigElementError("User {} does not exist.".format(user))

        return self.__user_output[user]
