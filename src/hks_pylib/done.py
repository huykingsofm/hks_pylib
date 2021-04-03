class Done(object):
    def __init__(self, value, **kwargs):
        self.value = value
        self.__attributes = {}

        self.__attributes.update(kwargs)

        if self.__attributes is not None:
            for key in self.__attributes.keys():
                setattr(self, key, self.__attributes[key])

    def copy(self, other, overwrite: bool = True):
        assert isinstance(other, Done)
        assert isinstance(overwrite, bool)
        for key in other.__attributes.keys():
            if (key in self.__attributes.keys() and overwrite) or key not in self.__attributes.keys():
                self.__attributes[key] = other.__attributes[key]
                setattr(self, key, self.__attributes[key])

    def __eq__(self, o: object) -> bool:
        return o == self.value
