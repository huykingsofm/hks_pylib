from typing import Union
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from hkserror import HTypeError


class KeyGenerator(object):
    def __init__(self, keysize, algorithm = None) -> None:
        self._keysize = keysize

        self._alogrithm = hashes.SHA256()
        if algorithm:
            self._alogrithm = algorithm

    def pwd2key(self, material: Union[str, bytes]):
        if not isinstance(material, (str, bytes)):
            raise HTypeError("material", material, str, bytes)

        if isinstance(material, str):
            material = material.encode()

        return HKDF(
            algorithm=self._alogrithm,
            length=self._keysize,
            salt=None,
            info=b'handshake data',
        ).derive(material)
