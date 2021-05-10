from hks_pylib import as_object

@as_object.paramterize(b=2)
class A():
    def __init__(self, b) -> None:
        self._b = b

    def print(self, a):
        print(a, self._b)

def test_as_object():
    A.print(5)
