from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from hkserror.hkserror import HTypeError


class HKSHash(object):
    "Abstract class: NEVER USE"
    def __init__(self, **kwargs) -> None:
        super().__init__()

    def update(self, msg: bytes) -> None:
        raise NotImplementedError()

    def finalize(self, msg: bytes = None) -> bytes:
        raise NotImplementedError()

    def reset(self) -> None:
        raise NotImplementedError()

    @property
    def digest_size(self) -> int:
        raise NotImplementedError()


class BuiltinHash(HKSHash):
    def __init__(self, algorithm: hashes.HashAlgorithm) -> None:
        if not isinstance(algorithm, hashes.HashAlgorithm):
            raise HTypeError("algorithm", algorithm, hashes.HashAlgorithm)

        self._algorithm = algorithm
        self._digest = hashes.Hash(self._algorithm, default_backend())
    
    def update(self, msg: bytes):
        if not isinstance(msg, bytes):
            raise HTypeError("msg", msg, bytes)

        self._digest.update(msg)
   
    def finalize(self, msg: bytes = None) -> bytes:
        if msg is not None and not isinstance(msg, bytes):
            raise HTypeError("msg", msg, bytes, None)

        if msg is not None:
            self.update(msg)

        return self._digest.finalize()

    def reset(self):
        self._digest = hashes.Hash(self._algorithm, default_backend())

    @property
    def digest_size(self) -> int:
        return self._algorithm.digest_size


class SHA256(BuiltinHash):
    def __init__(self) -> None:
        super().__init__(algorithm=hashes.SHA256())


class SHA1(BuiltinHash):
    def __init__(self) -> None:
        super().__init__(algorithm=hashes.SHA1())
