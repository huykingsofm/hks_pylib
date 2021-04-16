from typing import Any


from hks_pylib.hksenum import HKSEnum


class CipherProcess(HKSEnum):
    ENCRYPT = "Encrypt"
    DECRYPT = "Decrypt"
    FINALIZED = "Finalized"
    NONE = "None"

class HKSCipher(object):
    "Abstract class: NEVER USE"
    def __init__(self, key: Any = None, number_of_params: int = 0):
        self._key = key
        self._number_of_params = number_of_params

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        raise NotImplementedError()

    def decrypt(self, plaintext: bytes, finalize=True) -> bytes:
        raise NotImplementedError()

    def finalize(self) -> bytes:
        raise NotImplementedError()

    def set_param(self, index: int, value: bytes) -> None:
        raise NotImplementedError()

    def get_param(self, index: int) -> bytes:
        raise NotImplementedError()

    def reset(self, auto_renew_params: bool = True) -> None:
        raise NotImplementedError()
