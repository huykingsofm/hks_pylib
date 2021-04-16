from enum import Enum
from typing import Type

from hks_pylib.errors import InvalidParameterError


class HKSEnum(Enum):
    "A placeholder class"
    pass


class _Default(HKSEnum):
    "A placeholder class"
    unknown = "UNKNOWN"


class HKSEnum(Enum):
    @classmethod
    def values(cls):
        try:
            cls.__values
            return cls.__values
        except:
            cls.__values = []
            for e in cls:
                cls.__values.append(e.value)
            return cls.__values

    @classmethod
    def names(cls):
        try:
            cls.__names
            return cls.__names
        except:
            cls.__names = []
            for e in cls:
                cls.__names.append(e.name)
            return cls.__names

    @classmethod
    def get(cls, obj: object, default: object = _Default.unknown):
        return get_enum(cls, obj, default)


class Default(HKSEnum):
    unknown = "UNKNOWN"


unknown = Default.unknown


def get_enum(cls: Type[Enum], obj: object, default: object = unknown):
    if not issubclass(cls, Enum):
        raise InvalidParameterError("Parameter cls must be a subclass of Enum.")

    if default == _Default.unknown:
        default = Default.unknown

    for e in cls:
        if e.value == obj or e == obj:
            return e

    return default
