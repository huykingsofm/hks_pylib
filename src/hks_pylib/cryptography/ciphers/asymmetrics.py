from hks_pylib.math import ceil_div
from hks_pylib.hksenum import HKSEnum

from hks_pylib.cryptography.ciphers.cipherid import CipherID
from hks_pylib.cryptography.ciphers import HKSCipher, CipherProcess

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

from hks_pylib.errors import InvalidParameterError, UnknownHKSError
from hks_pylib.errors.cryptography.ciphers import NotFinalizeCipherError
from hks_pylib.errors.cryptography.ciphers import InvalidCipherParameterError
from hks_pylib.errors.cryptography.ciphers import NotExistKeyError, NotResetCipherError
from hks_pylib.errors.cryptography.ciphers.asymmetrics import InvalidEncodingError


class Encoding(HKSEnum):
    PEM = serialization.Encoding.PEM
    DER = serialization.Encoding.DER


class RSAKey(object):
    def __init__(self, encoding: str = Encoding.PEM.value) -> None:
        super().__init__()
        if encoding not in Encoding.values():
            raise InvalidParameterError("Parameter encoding must be an value "
            "in {} (e.g. Encoding.PEM.value).".format(Encoding.values()))

        self._encoding = encoding
        self.__private_key = None
        self.__public_key = None

    def generate(self, keysize, e=65537):
        if keysize < 1024:
            raise InvalidParameterError("Expected a larger rsa key (>=1024 bytes).")

        self.__private_key = rsa.generate_private_key(
            public_exponent=e,
            key_size=keysize,
            backend=default_backend()
        )
        
        self.__public_key = self.__private_key.public_key()

    @property
    def private_key(self) -> rsa.RSAPrivateKeyWithSerialization:
        return self.__private_key
    
    @property
    def public_key(self) -> rsa.RSAPublicKeyWithSerialization:
        return self.__public_key

    @property
    def key_size(self):
        if not self.__private_key and not self.__public_key:
            raise NotExistKeyError("Please import (generate/load/deserialize) "
            "a key before getting key_size.")
    
        if self.__private_key:
            return self.__private_key.key_size

        if self.__public_key:
            return self.__public_key.key_size

    def serialize_private_key(self, password: bytes = None):
        if password is None:
            _format = serialization.PrivateFormat.TraditionalOpenSSL
            encryption_algorithm = serialization.NoEncryption()
        else:
            _format = serialization.PrivateFormat.PKCS8
            encryption_algorithm = serialization.BestAvailableEncryption(password)

        return self.__private_key.private_bytes(
            encoding=self._encoding,
            format=_format,
            encryption_algorithm=encryption_algorithm
        )

    def deserialize_private_key(self, data: bytes, password: bytes = None):
        if self._encoding == serialization.Encoding.PEM:
            _load_private_key = serialization.load_pem_private_key
        elif self._encoding == serialization.Encoding.DER:
            _load_private_key = serialization.load_der_private_key
        else:
            raise InvalidEncodingError("Invalid encoding ({}), please choose an encoding in "
            "hks_pylib.cryptography.ciphers.asymmetrics.Encoding.".format(self._encoding))
        
        self.__private_key = _load_private_key(
            data=data,
            password=password,
        )

    def save_private_key(self, filename, password: bytes = None):
        data = self.serialize_private_key(password)
        with open(filename, "wb") as f:
            f.write(data)

    def load_private_key(self, filename, password: bytes = None):
        with open(filename, "rb") as key_file:
            self.deserialize_private_key(key_file.read(), password)

    def serialize_public_key(self):
        return self.__public_key.public_bytes(
            encoding=self._encoding,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def deserialize_public_key(self, data: bytes):
        if self._encoding == serialization.Encoding.PEM:
            _load_public_key = serialization.load_pem_public_key
        elif self._encoding == serialization.Encoding.DER:
            _load_public_key = serialization.load_der_public_key
        else:
            raise InvalidEncodingError("Invalid encoding ({}), please choose an encoding in "
            "hks_pylib.cryptography.ciphers.asymmetrics.Encoding.".format(self._encoding))

        self.__public_key = _load_public_key(data=data)

    def save_public_key(self, filename):
        data = self.serialize_private_key()
        with open(filename, "wb") as f:
            f.write(data)

    def load_public_key(self, filename):
        with open(filename, "rb") as key_file:
            self.deserialize_public_key(key_file.read())

    def save_all(self, directory: str, password: bytes = None):
        raise NotImplementedError("Please implement save_all() when you have time.")

    def load_all(self, directory: str, password: bytes = None):
        raise NotImplementedError("Please implement load_all() when you have time.")
        

@CipherID.register
class RSACipher(HKSCipher):
    def __init__(self,
                key: RSAKey,
                hash_algorithm: hashes.HashAlgorithm = hashes.SHA256
            ) -> None:
        if not isinstance(key, RSAKey):
            raise InvalidParameterError("Parameter key must be a RSAKey object.")

        super().__init__(key, number_of_params=0)
        self._key: RSAKey
        self._hash_algorithm = hash_algorithm

        self._in_process: CipherProcess = CipherProcess.NONE

        self._keysize = ceil_div(self._key.key_size, 8)

        # cryptography.rsa only accepts a small enough size of plaintext.
        # I refered the Maarten Bodewes's answer in the topic at
        # https://crypto.stackexchange.com/questions/42097/what-is-the-maximum-size-of-the-plaintext-message-for-rsa-oaep
        self._max_plaintext_size = self._keysize - 2 * self._hash_algorithm.digest_size - 2
        
        self._data = None

    def _raw_encrypt(self, plaintext: bytes):
        ciphertext = self._key.public_key.encrypt(
                plaintext,
                padding.OAEP(
                    mgf=padding.MGF1(self._hash_algorithm()),
                    algorithm=self._hash_algorithm(),
                    label=None
                ),
            )
        return ciphertext

    def _raw_decrypt(self, ciphertext: bytes):
        plaintext = self._key.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=self._hash_algorithm()),
                algorithm=self._hash_algorithm(),
                label=None
            )
        )
        return plaintext

    def encrypt(self, plaintext: bytes, finalize: bool = True):
        if not isinstance(plaintext, bytes):
            raise InvalidParameterError("Parameter plaintext must be a bytes object.")

        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.ENCRYPT
            self._data = b""

        if self._in_process is not CipherProcess.ENCRYPT:
            raise NotResetCipherError("You are in {} process, please call reset() "
            "before calling encrypt().".format(self._in_process.name))

        self._data += plaintext

        ciphertext = b""
        while len(self._data) > self._max_plaintext_size:
            data_to_enc = self._data[ : self._max_plaintext_size]
            self._data = self._data[self._max_plaintext_size : ]

            ciphertext += self._raw_encrypt(data_to_enc)

        if finalize:
            ciphertext += self.finalize()

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize: bool = True):
        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.DECRYPT
            self._data = b""

        if self._in_process is not CipherProcess.DECRYPT:
            raise NotResetCipherError("You are in {} process, please call reset() "
            "before calling decrypt().".format(self._in_process.name))

        self._data += ciphertext

        plaintext = b""
        while len(self._data) > self._keysize:
            data_to_dec = self._data[ : self._keysize]
            self._data = self._data[self._keysize : ]

            plaintext += self._raw_decrypt(data_to_dec)

        if finalize:
            plaintext += self.finalize()

        return plaintext

    def finalize(self) -> bytes:
        if self._in_process is CipherProcess.ENCRYPT:
            if len(self._data) > self._max_plaintext_size:
                raise UnknownHKSError("The size of remaining plaintext is too "
                "large (expected <= {} bytes, but passed {} "
                "bytes.)".format(self._max_plaintext_size, len(self._data)))

            finaltext = self._raw_encrypt(self._data)

        elif self._in_process is CipherProcess.DECRYPT:            
            if len(self._data) > self._keysize:
                raise UnknownHKSError("The size of remaining ciphertext is too "
                "large (expected <= {} bytes, but passed {} "
                "bytes.)".format(self._keysize, len(self._data)))

            finaltext = self._raw_decrypt(self._data)

        elif self._in_process is CipherProcess.FINALIZED:
            raise NotResetCipherError("Unknown process in your object "
            "({}).".format(self._in_process.name))
        else:
            raise UnknownHKSError("Unknown process ({}).".format(self._in_process.name))

        self._data = None
        self._in_process = CipherProcess.FINALIZED
        return finaltext

    def set_param(self, index: int, value: bytes) -> None:
        raise InvalidCipherParameterError("RSA has no parameter.")

    def get_param(self, index: int, value: bytes) -> None:
        raise InvalidCipherParameterError("RSA has no parameter.")

    def reset(self, auto_renew_params: bool = True) -> bool:
        if self._in_process not in (CipherProcess.NONE, CipherProcess.FINALIZED):
            raise NotFinalizeCipherError("Please finalize() the process before calling reset().")

        self._in_process = CipherProcess.NONE
        self._data = b""
