from hks_pylib.hksenum import HKSEnum, unknown


class Animal(HKSEnum):
    CAT = 1
    DOG = 2

def test_hksenum():
    assert Animal.names() == ["CAT", "DOG"]
    assert Animal.values() == [1, 2]

    assert Animal.get(1) == Animal.CAT
    assert Animal.get(3) == unknown
    assert Animal.get(2).value == Animal.DOG.value
    assert Animal.get(0, None) == None

    assert isinstance(Animal.CAT, HKSEnum)
    assert isinstance(unknown, HKSEnum)
