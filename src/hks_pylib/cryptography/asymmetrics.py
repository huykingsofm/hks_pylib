from hks_pylib.cryptography._cipher import HKSCipher
from hks_pylib.cryptography.cipherid import CipherID

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

from hks_pylib.math import ceil_div

ENCODING = (serialization.Encoding.PEM, serialization.Encoding.DER)

class RSAKey(object):
    def __init__(self, encoding: str = ENCODING[0]) -> None:
        super().__init__()
        if encoding not in ENCODING:
            raise Exception("encoding must be an element in {}".format(ENCODING))

        self._encoding = encoding
        self.__private_key = None
        self.__public_key = None

    def generate(self, keysize, e=65537):
        assert keysize >= 1024, "Expected a larger rsa key (>=1024 bytes)"

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
        if self.__private_key:
            return self.__private_key.key_size
        
        if self.__public_key:
            return self.__public_key.key_size
        
        raise Exception("Please import (generate/load/deserialize) a key before getting key_size")

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
            raise Exception("Invalid encoding ({}), expected {}".format(self._encoding, ENCODING))
        
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
            raise Exception("Invalid encoding ({}), expected {}".format(self._encoding, ENCODING))

        self.__public_key = _load_public_key(data=data)

    def save_public_key(self, filename):
        data = self.serialize_private_key()
        with open(filename, "wb") as f:
            f.write(data)

    def load_public_key(self, filename):
        with open(filename, "rb") as key_file:
            self.deserialize_public_key(key_file.read())

    def save_all(self, directory: str, password: bytes = None):
        pass

    def load_all(self, directory: str, password: bytes = None):
        pass
        

@CipherID.register
class RSACipher(HKSCipher):
    def __init__(self, key: RSAKey) -> None:
        super().__init__(key, number_of_params=0)
        self._key: RSAKey

        self._in_process = None
        self._keysize = ceil_div(self._key.key_size, 8)
        self._max_plaintext = self._keysize - 2 * hashes.SHA256.digest_size - 2
        self._data = b""

    def _encrypt(self, plaintext: bytes):
        ciphertext = self._key.public_key.encrypt(
                plaintext,
                padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                ),
            )
        return ciphertext

    def _decrypt(self, ciphertext: bytes):
        plaintext = self._key.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    def encrypt(self, plaintext: bytes, finalize: bool = True):
        if self._in_process is None:
            self._in_process = "encrypt"

        if self._in_process != "encrypt":
            raise Exception("You are in {} process, please finalize before calling encrypt()".
                format(self._in_process))

        self._data += plaintext

        ciphertext = b""
        while len(self._data) > self._max_plaintext:
            data_to_enc, self._data = self._data[:self._max_plaintext], self._data[self._max_plaintext:]
            ciphertext += self._encrypt(data_to_enc)

        if finalize:
            ciphertext += self._encrypt(self._data)
            self._data = b""
            self._in_process = None

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize: bool = True):
        if self._in_process is None:
            self._in_process = "decrypt"

        if self._in_process != "decrypt":
            raise Exception("You are in {} process, please finalize before calling decrypt()".
                format(self._in_process))

        self._data += ciphertext

        plaintext = b""
        while len(self._data) > self._keysize:
            data_to_dec, self._data = self._data[:self._keysize], self._data[self._keysize:]
            plaintext += self._decrypt(data_to_dec)

        if finalize:
            plaintext += self._decrypt(self._data)
            self._data = b""
            self._in_process = None

        return plaintext

    def set_param(self, index: int, value: bytes) -> None:
        raise Exception("RSA has no parameter")

    def get_param(self, index: int, value: bytes) -> None:
        raise Exception("RSA has no parameter")

    def reset(self, auto_renew_params: bool = True) -> bool:
        pass
