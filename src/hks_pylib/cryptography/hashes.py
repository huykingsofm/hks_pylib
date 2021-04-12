from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


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
    def __init__(self, **kwargs) -> None:
        self._algorithm = kwargs.pop("algorithm", None)
        if kwargs:
            raise Exception("Unexpected paramters {}".format(set(kwargs.keys())))
        self._digest = hashes.Hash(self._algorithm, default_backend())
    
    def update(self, msg: bytes):
        self._digest.update(msg)
   
    def finalize(self, msg: bytes = None) -> bytes:
        if msg is not None:
            self.update(msg)
        return self._digest.finalize()

    def reset(self):
        self._digest = hashes.Hash(self._algorithm, default_backend())

    @property
    def digest_size(self) -> int:
        return self._algorithm.digest_size

class SHA256(BuiltinHash):
    def __init__(self, **kwargs) -> None:
        super().__init__(algorithm=hashes.SHA256())

class SHA1(BuiltinHash):
    def __init__(self, **kwargs) -> None:
        super().__init__(algorithm=hashes.SHA1())
