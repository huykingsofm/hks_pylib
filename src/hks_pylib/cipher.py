import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


def hash_cls_name(name):
    if type(name).__name__ == 'type' or type(name).__name__ == 'builtin_function_or_method':
        name = str(name).split(".")[-1][:-2].encode()
    else:
        name = type(name).__name__.encode()
    hash_value = name[0]
    for c in name[1:]:
        hash_value = hash_value ^ c

    hash_byte1 = hash_value.to_bytes(1, "big")
    hash_byte2 = (hash_value ^ len(name)).to_bytes(1, "big")
    return hash_byte1 + hash_byte2


class CipherException(Exception): ...
class EncryptFailed(CipherException): ...
class DecryptFailed(CipherException): ...
class UnAuthenticatedPacket(DecryptFailed): ...


class _Cipher(object):
    "Abstract class: NEVER USE"
    def __init__(self, key: bytes = None, number_of_params: int = 0):
        self.key = key
        self.number_of_params = number_of_params

    def set_new_key(self, newkey: bytes) -> bool:
        raise NotImplementedError

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes: 
        raise NotImplementedError

    def decrypt(self, plaintext: bytes, finalize=True) -> bytes:
        raise NotImplementedError

    def set_param(self, index: int, value: bytes) -> None:
        raise NotImplementedError

    def get_param(self, index: int) -> bytes:
        raise NotImplementedError

    def reset_params(self) -> bool:
        raise NotImplementedError


class NoCipher(_Cipher):
    "Do not encrypt the message"
    def set_new_key(self, newkey):
        # Do nothing
        return True

    def encrypt(self, plaintext, finalize=True):
        return plaintext

    def decrypt(self, ciphertext, finalize=True):
        return ciphertext

    def set_param(self, index, value):
        raise Exception("Index exceeds (NoCipher doesn't use any parameters")

    def get_param(self, index):
        raise Exception("Index exceeds (NoCipher doesn't use any parameters")

    def reset_params(self):
        # Do nothing
        pass


class XorCipher(_Cipher):
    "Encrypt the payload using xor operator: c = p xor key"
    def __init__(self, key: bytes):
        if not isinstance(key, bytes) or len(key) != 1:
            raise Exception("Key of XorCipher must a bytes object of length 1")
        key = key[0]

        super().__init__(key, 1)

    def set_new_key(self, newkey: bytes):
        if not isinstance(newkey, bytes) or len(newkey) != 1:
            raise Exception("Key of XorCipher must a bytes object of length 1")

        self.key = newkey[0]

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if not isinstance(plaintext, bytes):
            raise Exception("Plain text must be a bytes object")

        if not hasattr(self, "iv"):
            raise EncryptFailed("IV has not been set yet")

        ciphertext = b''
        for c in plaintext:
            ciphertext += int.to_bytes(c ^ self.key ^ self.iv, 1, "big")

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if not isinstance(ciphertext, bytes):
            raise Exception("Cipher text must be a bytes object")

        return self.encrypt(ciphertext)

    def set_param(self, index: int, value: bytes) -> None:
        if not isinstance(value, bytes):
            raise Exception("Value must be a bytes object")

        if index == 0:
            if len(value) != 1:
                raise Exception("IV of XorCipher must be an 1-length bytes object")
            else:
                self.iv = value[0]
        else:
            raise Exception("Index exceeds (XorCipher use only one parameter)")

    def get_param(self, index: int) -> bytes:
        if index == 0:
            return self.iv.to_bytes(1, "big")

        raise Exception("XorCipher use only one parameter")

    def reset_params(self):
        newiv = os.urandom(1)
        if self.set_param(0, newiv) is False:
            return False
        return True


class AES_CTR(_Cipher):
    def __init__(self, key: bytes):
        if len(key) * 8 not in [128, 192, 256, 512]:
            raise Exception("Key size of AES must be in {128, 192, 256, 512}")
        super().__init__(key, 1)

    def set_new_key(self, newkey: bytes):
        if len(newkey) * 8 not in [128, 192, 256, 512]:
            raise Exception("Key size of AES must be in {128, 192, 256, 512}")
        self.key = newkey

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if not isinstance(plaintext, bytes):
            raise Exception("Plain text must be a bytes object")

        if not hasattr(self, "encryptor"):
            raise EncryptFailed("Nonce has not been set yet")
        try:
            ciphertext = self.encryptor.update(plaintext)
            if finalize:
                ciphertext += self.encryptor.finalize()
        except Exception as e:
            raise e

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if not isinstance(ciphertext, bytes):
            raise Exception("Cipher text must be a bytes object")

        if not hasattr(self, "decryptor"):
            raise EncryptFailed("Nonce has not been set yet")
        try:
            plaintext = self.decryptor.update(ciphertext)
            if finalize:
                plaintext += self.decryptor.finalize()
        except Exception as e:
            raise e

        return plaintext

    def set_param(self, index: int, param: bytes) -> None:
        if not isinstance(param, bytes):
            raise Exception("Parameters of AES must be a bytes object")

        if index == 0:
            if len(param) != 16:
                raise Exception("Invalid length of nonce value, expected 16 bytes")

            self.nonce = param
            aes = Cipher(algorithms.AES(self.key), modes.CTR(self.nonce), default_backend())
            self.encryptor = aes.encryptor()
            self.decryptor = aes.decryptor()
        else:
            raise Exception("AES only use the nonce value as its parameter")

    def get_param(self, index) -> bytes:
        if index == 0:
            return self.nonce
        else:
            raise Exception("AES only use the nonce value as its parameter")

    def reset_params(self):
        new_nonce = os.urandom(16)
        if not self.set_param(0, new_nonce):
            return False
        return True


class AES_CBC(_Cipher):
    def __init__(self, key: bytes):
        if len(key) * 8 not in [128, 192, 256, 512]:
            raise Exception("Key size of AES must be in {128, 192, 256, 512}")
        super().__init__(key, 1)

    def set_new_key(self, newkey: bytes):
        if len(newkey) * 8 not in [128, 192, 256, 512]:
            raise Exception("Key size of AES must be in {128, 192, 256, 512}")
        self.key = newkey

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if not isinstance(plaintext, bytes):
            raise Exception("Plain text must be a bytes object")

        if not hasattr(self, "encryptor"):
            raise EncryptFailed("IV has not been set yet")
        try:
            padded_text = self.padder.update(plaintext)
            if finalize:
                padded_text += self.padder.finalize()

            ciphertext = self.encryptor.update(padded_text)
            if finalize:
                ciphertext += self.encryptor.finalize()
        except Exception as e:
            raise e

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if not isinstance(ciphertext, bytes):
            raise Exception("Cipher text must be a bytes object")

        if not hasattr(self, "decryptor"):
            raise EncryptFailed("IV has not been set yet")
        try:
            padded_text = self.decryptor.update(ciphertext)
            if finalize:
                padded_text += self.decryptor.finalize()

            plaintext = self.unpadder.update(padded_text)
            if finalize:
                plaintext += self.unpadder.finalize()
        except Exception as e:
            raise e

        return plaintext

    def set_param(self, index: int, param: bytes) -> None:
        if not isinstance(param, bytes):
            raise Exception("Parameters of AES must be a bytes object")

        if index == 0:
            if len(param) != 16:
                raise Exception("Invalid length of iv value, expected 16 bytes")

            self.iv = param
            aes = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), default_backend())
            self.encryptor = aes.encryptor()
            self.decryptor = aes.decryptor()

            self.padder = padding.PKCS7(128).padder()
            self.unpadder = padding.PKCS7(128).unpadder()
        else:
            raise Exception("AES only use the iv value as its parameter")

    def get_param(self, index) -> bytes:
        if index == 0:
            return self.iv
        else:
            raise Exception("AES only use the iv value as its parameter")

    def reset_params(self):
        new_iv = os.urandom(16)
        if not self.set_param(0, new_iv):
            return False
        return True


class SimpleSSL(_Cipher):
    def __init__(self, cipher: _Cipher, hashfunc=hashlib.sha256):
        super().__init__(None, cipher.number_of_params)
        self.cipher = cipher
        self.hashfunc = hashfunc
        self.digest_length = self.hashfunc(b"").digest_size

    def set_new_key(self, newkey: bytes):
        return self.cipher.set_new_key(newkey)

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        hashvalue = self.hashfunc(plaintext).digest()

        authenticated_plaintext = plaintext + hashvalue
        return self.cipher.encrypt(authenticated_plaintext, finalize)

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        authenticated_plaintext = self.cipher.decrypt(ciphertext, finalize)
        plaintext = authenticated_plaintext[:-self.digest_length]
        hashvalue = authenticated_plaintext[-self.digest_length:]
        if self.hashfunc(plaintext).digest() == hashvalue:
            return plaintext
        else:
            raise UnAuthenticatedPacket("Packet authentication failed")

    def set_param(self, index: int, param: bytes) -> None:
        return self.cipher.set_param(index, param)

    def get_param(self, index: int) -> bytes:
        return self.cipher.get_param(index)

    def reset_params(self):
        return self.cipher.reset_params()


class AllCipher(object):
    _cipher_hashs = {}
    _cipher_names = {}
    _cipher_hashs_invert = {}
    _cipher_names_invert = {}

    @staticmethod
    def register(cipher_cls):
        assert issubclass(cipher_cls, _Cipher)
        AllCipher._cipher_hashs[hash_cls_name(cipher_cls)] = cipher_cls
        AllCipher._cipher_names[cipher_cls.__name__] = cipher_cls
        AllCipher._cipher_hashs_invert[cipher_cls] = hash_cls_name(cipher_cls)
        AllCipher._cipher_names_invert[cipher_cls] = cipher_cls.__name__

    @staticmethod
    def hash2cls(hash_value):
        return AllCipher._cipher_hashs.get(hash_value, None)

    @staticmethod
    def name2cls(name):
        return AllCipher._cipher_names.get(name, None)

    @staticmethod
    def cls2hash(cipher_cls):
        return AllCipher._cipher_hashs_invert.get(cipher_cls, None)

    @staticmethod
    def cls2name(cipher_cls):
        return AllCipher._cipher_names_invert.get(cipher_cls, None)
