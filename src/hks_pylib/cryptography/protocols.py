from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import dh

from hks_pylib.errors import InvalidParameterError
from hks_pylib.errors.cryptography.protocols import NotResetProtocolError


class DiffieHellmanExchange(object):
    DEFAULT_P = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
    DEFAULT_G = 2

    def __init__(self, p: int = None, g: int = None) -> None:
        if p is not None and not isinstance(p, int):
            raise InvalidParameterError("Parameter p must be None or a int object.")
        
        if g is not None and not isinstance(g, int):
            raise InvalidParameterError("Parameter g must be None or a int object.")

        if not p:
            p = DiffieHellmanExchange.DEFAULT_P
        if not g:
            g = DiffieHellmanExchange.DEFAULT_G

        params_numbers = dh.DHParameterNumbers(p, g)
        self._parameters = params_numbers.parameters(default_backend())
        self.__private_key = self._parameters.generate_private_key()

    @property
    def public_key(self) -> dh.DHPublicKey:
        if self.__private_key is None:
            return None

        return self.__private_key.public_key()

    def exchange(self, public_key: dh.DHPublicKey) -> bytes:
        if not isinstance(public_key, dh.DHPublicKey):
            raise InvalidParameterError("Parameter public key must be a DHPublicKey object.")

        if self.__private_key is None:
            raise NotResetProtocolError("You must call reset() the DHE before call exchange().")

        common_key = self.__private_key.exchange(public_key)
        self.__private_key = None
        return common_key

    def reset(self):
        self.__private_key = self._parameters.generate_private_key()

    @staticmethod
    def derive_key(shared_key: bytes, key_size: int) -> bytes:
        if not isinstance(shared_key, bytes):
            raise InvalidParameterError("Parameter shared_key must be a bytes object.")

        if not isinstance(key_size, int):
            raise InvalidParameterError("Parameter key_size must be a int.")

        return HKDF(
            algorithm=hashes.SHA256(),
            length=key_size,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)
