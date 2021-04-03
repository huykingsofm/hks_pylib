import pytest
from hks_pylib.done import Done


def test():
    done1 = Done(True, author="huykingsofm")
    done2 = Done(False, author="hks")
    done2.copy(done1, True)
    assert done2.author == "huykingsofm"
