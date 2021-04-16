from typing import Optional
from hks_pylib.errors import InvalidParameterError


class Done(object):
    def __init__(self, value: Optional[object] = None, **kwargs):
        self.value = value
        self.__attributes = {}

        self.__attributes.update(kwargs)

        for key in self.__attributes.keys():
            setattr(self, key, self.__attributes[key])

    def copy(self, other, overwrite: bool = True):
        if not isinstance(other, Done):
            raise InvalidParameterError("Parameter other must be a Done object.")

        for key in other.__attributes.keys():
            if (key in self.__attributes.keys() and overwrite) or (key not in self.__attributes.keys()):
                self.__attributes[key] = other.__attributes[key]
                setattr(self, key, self.__attributes[key])

    def has(self, attr: str):
        return hasattr(self, attr)

    def __eq__(self, o: object) -> bool:
        return o == self.value

    def __str__(self) -> str:
        return str(self.__attributes)
