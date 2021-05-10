from typing import Any, Type


class AsObject():
    def __init__(self) -> None:
        self.__args = ()
        self.__kwargs = {}

    def paramterize(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        return self

    def __call__(self, cls: Type):
        obj = cls(*self.__args, **self.__kwargs)
        self.__init__()
        return obj


as_object = AsObject()
