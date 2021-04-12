import os
import datetime
import threading


class LogConfig(object):
    def __init__(self) -> None:
        super().__init__()
        self.__user_level = {}
        self.__user_output = {}
        self.lock = threading.Lock()

    def add_user(self, user: str):
        assert isinstance(user, str)
        assert user not in self.__user_level.keys()
        self.__user_level[user] = set()
        self.__user_output[user] = None, None  # --> os.sys.stdout

    def _add_level_one_element(self, user: str, level: str):
        assert isinstance(user, str)
        assert isinstance(level, str)
        assert user in self.__user_level.keys()
        assert level not in self.__user_level[user]
        self.__user_level[user].add(level)

    def add_level(self, user: str, *levels):
        assert len(levels) > 0
        for level in levels:
            self._add_level_one_element(user, level)

    def set_output(self, user: str, file_name: str, mode: str = "a"):
        assert isinstance(user, str)
        assert isinstance(file_name, str)
        assert mode in ("a", "w")
        assert user in self.__user_output.keys()
        self.__user_output[user] = file_name, mode

    def __contains__(self, user: str):
        return user in self.__user_level.keys()

    def user(self):
        return set(self.__user_level.keys())

    def level(self, user: str):
        if user in self.__user_level.keys():
            return self.__user_level[user]

    def output(self, user: str):
        if user in self.__user_output.keys():
            return self.__user_output[user]


class BaseLogger(object):
    def __init__(self, name, config: LogConfig, display):
        self._config = config
        self._display = display

        for user in self._display:
            if user not in self._config:
                raise Exception(f"Displayed user must be in {self._config.user()}, rather than {user}")
            
            if self._display[user] == ["ALL"]:
                continue
            
            for level in self._display[user]:
                if level not in self._config.level(user):
                    raise Exception(
                        f"Displayed level of '{user}' must be in the {self._config.level(user)}, rather than {level}")

        self.__name = name

    def __call__(self, user, level, *values, **kwargs):
        if user not in self._config:
            raise Exception(f"User must be in {list(self._config.user())}, rather than {user}")

        if level not in self._config.level(user):
            raise Exception(f"Level of '{user}' must be in {self._config.level(user)}, rather than {level}")

        if user not in self._display:
            return

        if self._display[user] != ["ALL"] and level not in self._display[user]:
            return

        self._config.lock.acquire()
        output = self._config.output(user)
        if output[0] is None:
            file = os.sys.stdout
        else:
            file = open(output[0], output[1])

        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if self.__name:
            print(f"{now} {level.upper()} [{self.__name}] -", *values, file=file, **kwargs)
        else:
            print(f"{now} {level.upper()} -", *values, file=file, **kwargs)

        if output[0] is not None:
            file.close()

        self._config.lock.release()

    def use_dict(self, print_dict: dict):
        for user in print_dict.keys():
            for level in print_dict[user]:
                self.__call__(user, level, print_dict[user][level])


class StandardLogger(BaseLogger):
    def __init__(self, name, log_file_name: str, display):
        config = LogConfig()
        config.add_user("user")
        config.add_level("user", "info", "warning")
        config.add_user("dev")
        config.add_level("dev", "info", "warning", "error", "debug", "critical")
        config.set_output("dev", log_file_name)
        super().__init__(name, config, display)


class LoggerGenerator(object):
    def __init__(self, logger_cls, **kwargs) -> None:
        super().__init__()
        self._logger_cls = logger_cls
        self._logger_kwargs = kwargs

    def generate(self, name, display):
        return self._logger_cls(name=name, display=display, **self._logger_kwargs)


class StandardLoggerGenerator(LoggerGenerator):
    def __init__(self, log_file_name: str) -> None:
        self._config = LogConfig()
        self._config.add_user("user")
        self._config.add_level("user", "info", "warning")
        self._config.add_user("dev")
        self._config.add_level("dev", "info", "warning", "error", "debug", "critical")
        self._config.set_output("dev", log_file_name)

        super().__init__(BaseLogger, config=self._config)
