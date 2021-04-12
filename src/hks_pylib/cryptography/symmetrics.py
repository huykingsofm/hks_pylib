import os

from hks_pylib.math import bxor

from hks_pylib.cryptography.cipherid import CipherID
from hks_pylib.cryptography._cipher import HKSCipher
from hks_pylib.cryptography.hashes import SHA256, HKSHash

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class CipherException(Exception): ...
class EncryptFailed(CipherException): ...
class DecryptFailed(CipherException): ...
class UnAuthenticatedPacket(DecryptFailed): ...


@CipherID.register
class NoCipher(HKSCipher):
    "Do not encrypt the message"
    def encrypt(self, plaintext, finalize=True):
        return plaintext

    def decrypt(self, ciphertext, finalize=True):
        return ciphertext
    
    def finalize(self) -> bytes:
        return b""

    def set_param(self, index, value):
        raise Exception("Index exceeds (NoCipher doesn't use any parameters")

    def get_param(self, index):
        raise Exception("Index exceeds (NoCipher doesn't use any parameters")

    def reset(self, auto_renew_params: bool = True):
        # Do nothing
        pass


@CipherID.register
class XorCipher(HKSCipher):
    "Encrypt the payload using xor operator: c = p xor key"
    def __init__(self, key: bytes):
        if not isinstance(key, bytes) :
            raise Exception("Key of XorCipher must a bytes object")

        super().__init__(key, 1)
        self._in_process = None
        self._data = None
        self._iv = None

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if self._in_process is None:
            self._in_process = "encrypt"
        
        if self._in_process != "encrypt":
            raise Exception("Please call reset() the cipher before calling encrypt()")

        if not isinstance(plaintext, bytes):
            raise Exception("Plain text must be a bytes object")

        if self._iv is None:
            raise EncryptFailed("IV has not been set yet")

        if not self._data:
            self._data = b""

        self._data += plaintext
        ciphertext = b""
        while len(self._data) > len(self._key):
            data_to_enc, self._data = self._data[:len(self._key)], self._data[len(self._key):]
            block = bxor(data_to_enc, self._key)
            ciphertext += bxor(block, self._iv)

        if finalize:
            ciphertext += self.finalize()

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if self._in_process is None:
            self._in_process = "decrypt"
        
        if self._in_process != "decrypt":
            raise Exception("Please call reset() the cipher before calling decrypt()")

        if not isinstance(ciphertext, bytes):
            raise Exception("Plain text must be a bytes object")

        if self._iv is None:
            raise EncryptFailed("IV has not been set yet")

        if not self._data:
            self._data = b""

        self._data += ciphertext
        plaintext = b""
        while len(self._data) > len(self._key):
            data_to_enc, self._data = self._data[:len(self._key)], self._data[len(self._key):]
            block = bxor(data_to_enc, self._key)
            plaintext += bxor(block, self._iv)

        if finalize:
            plaintext += self.finalize()

        return plaintext

    def finalize(self) -> bytes:
        ld = len(self._data)
        return bxor(self._data, self._key[:ld])

    def set_param(self, index: int, value: bytes) -> None:
        if not isinstance(value, bytes):
            raise Exception("Value must be a bytes object")

        if index == 0:
            if len(value) != len(self._key):
                raise Exception("IV of XorCipher must be a bytes object which is the same size as the key")
            else:
                self._iv = value
        else:
            raise Exception("Index exceeds (XorCipher use only one parameter)")

    def get_param(self, index: int) -> bytes:
        if index == 0:
            return self._iv

        raise Exception("XorCipher use only one parameter")

    def reset(self, auto_renew_params: bool = True):
        if auto_renew_params:
            newiv = os.urandom(len(self._key))
            self.set_param(0, newiv)
        else:
            self.set_param(0, self._iv)
        self._in_process = None
        self._data = None


@CipherID.register
class AES_CTR(HKSCipher):
    def __init__(self, key: bytes):
        if len(key) * 8 not in algorithms.AES.key_sizes:
            raise Exception("Key size of AES must be in {}, not {}".format(
                set(algorithms.AES.key_sizes),
                len(key) * 8
            ))

        super().__init__(key, number_of_params=1)
        self._aes = None
        self._encryptor = None
        self._decryptor = None

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if self._aes is None:
            raise Exception("Please set nonce before calling encrypt()")

        if self._decryptor is not None:
            raise Exception("Please reset() or finalize() the cipher before calling encrypt()")
    
        if not isinstance(plaintext, bytes):
            raise Exception("Plaintext must be a bytes object")

        if not self._encryptor:
            self._encryptor = self._aes.encryptor()

        ciphertext = self._encryptor.update(plaintext)

        if finalize:
            ciphertext += self.finalize()

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if self._aes is None:
            raise Exception("Please set nonce before calling decrypt()")

        if self._encryptor is not None:
            raise Exception("Please reset() or finalize() the cipher before calling decrypt()")

        if not isinstance(ciphertext, bytes):
            raise Exception("Ciphertext must be a bytes object")
    
        if not self._decryptor:
            self._decryptor = self._aes.decryptor()
        
        plaintext = self._decryptor.update(ciphertext)
        
        if finalize:
            plaintext += self.finalize()

        return plaintext

    def finalize(self) -> bytes:
        if self._encryptor is None and self._decryptor is None:
            raise Exception("Please call encrypt() or decrypt() before calling finalize()")

        if self._aes is None:
            raise Exception("Unknown error (_aes is None when calling finalize())")

        if self._encryptor and self._decryptor:
            raise Exception("Unknown error (encryptor and decrytor have both existed already)")

        if self._encryptor:
            return self._encryptor.finalize()
        
        if self._decryptor:
            return self._decryptor.finalize()

    def set_param(self, index: int, param: bytes) -> None:
        if not isinstance(param, bytes):
            raise Exception("Parameters of AES must be a bytes object")

        if index == 0:
            if len(param) * 8 != algorithms.AES.block_size:
                raise Exception("Invalid length of nonce value ({} bits),"
                    "expected less than {} bits".format(
                        len(param) * 8,
                        algorithms.AES.block_size
                ))

            self._nonce = param
            self._aes = Cipher(algorithms.AES(self._key), modes.CTR(self._nonce), default_backend())
        else:
            raise Exception("AES only use the nonce value as its parameter")

    def get_param(self, index) -> bytes:
        if index == 0:
            return self._nonce
        else:
            raise Exception("AES only use the nonce value as its parameter")

    def reset(self, auto_renew_params: bool = True):
        self._encryptor = None
        self._decryptor = None
        if auto_renew_params:
            new_nonce = os.urandom(algorithms.AES.block_size // 8)
        else:
            new_nonce = self._nonce
        return self.set_param(0, new_nonce)


@CipherID.register
class AES_CBC(HKSCipher):
    def __init__(self, key: bytes):
        if len(key) * 8 not in algorithms.AES.key_sizes:
            raise Exception("Key size of AES must be in {}, not {}".format(
                set(algorithms.AES.key_sizes),
                len(key) * 8
            ))
        super().__init__(key, number_of_params=1)
        self._aes = None
        self._encryptor = None
        self._decryptor = None

        self._pkcs7 = padding.PKCS7(128)
        self._padder = None
        self._unpadder = None

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if self._aes is None:
            raise Exception("Please set IV before calling encrypt()")

        if self._decryptor is not None or self._unpadder is not None:
            raise Exception("Please reset() or finalize() the cipher before calling encrypt()")

        if not isinstance(plaintext, bytes):
            raise Exception("Plaintext must be a bytes object")

        if not self._padder:
            self._padder = self._pkcs7.padder()
    
        if not self._encryptor:
            self._encryptor = self._aes.encryptor()

        text = self._padder.update(plaintext)
        ciphertext = self._encryptor.update(text)
        
        if finalize:
            ciphertext += self.finalize()

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if self._aes is None:
            raise Exception("Please set IV before calling decrypt()")

        if self._encryptor is not None or self._padder is not None:
            raise Exception("Please reset() or finalize() the cipher before calling decrypt()")

        if not isinstance(ciphertext, bytes):
            raise Exception("Ciphertext must be a bytes object")

        if not self._unpadder:
            self._unpadder = self._pkcs7.unpadder()

        if not self._decryptor:
            self._decryptor = self._aes.decryptor()

        padded_text = self._decryptor.update(ciphertext)
        plaintext = self._unpadder.update(padded_text)
        
        if finalize:
            plaintext += self.finalize()

        return plaintext

    def finalize(self) -> bytes:
        if self._encryptor is None and self._decryptor is None:
            raise Exception("Please call encrypt() or decrypt() before calling finalize()")

        if self._aes is None:
            raise Exception("Unknown error (_aes is None when calling finalize())")

        if self._encryptor and self._decryptor:
            raise Exception("Unknown error (encryptor and decrytor have both existed already)")

        if self._encryptor:
            text = self._padder.finalize()
            ciphertext = self._encryptor.update(text)
            ciphertext += self._encryptor.finalize()
            return ciphertext
        
        if self._decryptor:
            padded_text = self._decryptor.finalize()
            plaintext = self._unpadder.update(padded_text)
            plaintext += self._unpadder.finalize()
            return plaintext

    def set_param(self, index: int, param: bytes) -> None:
        if not isinstance(param, bytes):
            raise Exception("Parameters of AES must be a bytes object")

        if index == 0:
            if len(param) * 8 != algorithms.AES.block_size:
                raise Exception("Invalid length of IV value ({} bits), expected {} bits".
                    format(
                        len(param) * 8,
                        algorithms.AES.block_size
                    )
                )

            self._iv = param
            self._aes = Cipher(algorithms.AES(self._key), modes.CBC(self._iv), default_backend())
        else:
            raise Exception("AES CBC only use the IV value as its parameter")

    def get_param(self, index) -> bytes:
        if index == 0:
            return self._iv
        else:
            raise Exception("AES CBC only use the IV value as its parameter")

    def reset(self, auto_renew_params: bool = True):
        self._encryptor = None
        self._decryptor = None
        self._padder = None
        self._unpadder = None
        if auto_renew_params:
            new_iv = os.urandom(16)
        else:
            new_iv = self._iv
        self.set_param(0, new_iv)


@CipherID.register
class HybridCipher(HKSCipher):
    def __init__(self, cipher_obj: HKSCipher, hash_obj: HKSHash = SHA256()):
        super().__init__(None, cipher_obj._number_of_params)
        self._cipher = cipher_obj
        self._hash = hash_obj

        self._in_process = None

        self._stored_digest = None

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        "ciphertext = E(plaintext + hash(plaintext))"
        if self._in_process is None:
            self._in_process = "encrypt"

        if self._in_process != "encrypt":
            raise Exception("Please reset() the cipher before calling encrypt()")

        self._hash.update(plaintext)
        ciphertext = self._cipher.encrypt(plaintext, finalize=False)

        if finalize:
            ciphertext += self.finalize()

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if self._in_process is None:
            self._in_process = "decrypt"

        if self._in_process != "decrypt":
            raise Exception("Please reset() the cipher before calling decrypt()")
        
        if self._stored_digest is None:
            self._stored_digest = b""
        
        plaintext = self._cipher.decrypt(ciphertext, finalize=False)

        all_plaintext = self._stored_digest + plaintext

        actual_plaintext = all_plaintext[:-self._hash.digest_size]

        self._stored_digest = all_plaintext[-self._hash.digest_size:]

        self._hash.update(actual_plaintext)

        if finalize:
            actual_plaintext += self.finalize()

        return actual_plaintext

    def finalize(self) -> bytes:
        if self._in_process == "encrypt":
            msg_digest = self._hash.finalize()
            ciphertext = self._cipher.encrypt(msg_digest, finalize=True)
            return ciphertext
        elif self._in_process == "decrypt":
            plaintext = self._cipher.finalize()
            all_plaintext = self._stored_digest + plaintext

            actual_plaintext = all_plaintext[:-self._hash.digest_size]

            self._stored_digest = all_plaintext[-self._hash.digest_size:]

            self._hash.update(actual_plaintext)
            
            expected_digest = self._stored_digest
            computed_digest = self._hash.finalize()

            if expected_digest != computed_digest:
                raise UnAuthenticatedPacket("Packet authentication failed")
            
            return actual_plaintext
        else:
            raise Exception("Please call encrypt() or decrypt() before calling finalize()")

    def set_param(self, index: int, param: bytes) -> None:
        return self._cipher.set_param(index, param)

    def get_param(self, index: int) -> bytes:
        return self._cipher.get_param(index)

    def reset(self, auto_renew_params: bool = True):
        self._stored_digest = None
        self._in_process = None
        self._hash.reset()
        self._cipher.reset(auto_renew_params)
