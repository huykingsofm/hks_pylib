import os

from hkserror.hkserror import HTypeError
from hks_pylib.errors.cryptography.ciphers import KeyError

from hks_pylib.math import bxor

from hks_pylib.cryptography.hashes import SHA256, HKSHash
from hks_pylib.cryptography.ciphers.cipherid import CipherID
from hks_pylib.cryptography.ciphers import HKSCipher, CipherProcess

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, CipherContext, algorithms, modes

from hks_pylib.errors.cryptography import ResetError
from hks_pylib.errors.cryptography.ciphers import CipherParameterError
from hks_pylib.errors.cryptography.ciphers import FinalizeCipherError
from hks_pylib.errors.cryptography.ciphers import CipherParameterError
from hks_pylib.errors.cryptography.ciphers.symmetrics import SymmetricError, UnAuthenticatedPacketError


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
        raise CipherParameterError("Index exceeds (NoCipher doesn't use any parameters).")

    def get_param(self, index):
        raise CipherParameterError("Index exceeds (NoCipher doesn't use any parameters).")

    def reset(self, auto_renew_params: bool = True):
        # Do nothing
        pass


@CipherID.register
class XorCipher(HKSCipher):
    "Encrypt the payload using xor operator: c = p xor key"
    def __init__(self, key: bytes):
        if not isinstance(key, bytes) :
            raise HTypeError("key", key, bytes)

        super().__init__(key, 1)
        self._in_process: CipherProcess = CipherProcess.NONE
        self._data: bytes = None
        self._iv: bytes = None

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if not isinstance(plaintext, bytes):
            raise HTypeError("plaintext", plaintext, bytes)

        if not self._key:
            raise KeyError("Please provide key before calling encrypt()")

        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.ENCRYPT
            self._data = b""
        
        if self._in_process is not CipherProcess.ENCRYPT:
            raise ResetError("You are in {} process, please call reset() "
                "before calling encrypt().".format(self._in_process.name))

        if self._iv is None:
            raise CipherParameterError("IV has not been set yet.")

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
        if not isinstance(ciphertext, bytes):
            raise HTypeError("ciphertext", ciphertext, bytes)
  
        if not self._key:
            raise KeyError("Please provide key before calling decrypt()")

        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.DECRYPT
            self._data = b""
        
        if self._in_process is not CipherProcess.DECRYPT:
            raise ResetError("You are in {} process, please call reset() "
            "before calling decrypt().".format(self._in_process.name))

        if self._iv is None:
            raise CipherParameterError("IV has not yet been set.")

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
        finaltext = bxor(self._data, self._key[:ld])

        self._data = CipherProcess.FINALIZED
        return finaltext

    def set_param(self, index: int, value: bytes) -> None:
        if not isinstance(value, bytes):
            raise HTypeError("value", value, bytes)

        if index == 0:
            if len(value) != len(self._key):
                raise CipherParameterError("IV of XorCipher must be a bytes object "
                "which is the same size as the key.")
            else:
                self._iv = value
        else:
            raise CipherParameterError("Index exceeds (XorCipher use only one parameter).")

    def get_param(self, index: int) -> bytes:
        if index == 0:
            return self._iv

        raise CipherParameterError("XorCipher use only one parameter.")

    def reset(self, auto_renew_params: bool = True):
        if auto_renew_params:
            newiv = os.urandom(len(self._key))
            self.set_param(0, newiv)
        else:
            self.set_param(0, self._iv)
        self._in_process = CipherProcess.NONE
        self._data = None


@CipherID.register
class AES_CTR(HKSCipher):
    def __init__(self, key: bytes):
        if not isinstance(key, bytes):
            raise HTypeError("key", key, bytes)

        if len(key) * 8 not in algorithms.AES.key_sizes:
            raise CipherParameterError("Key size of AES must be in {} (bits), "
            "not {} (bytes).".format(
                set(algorithms.AES.key_sizes),
                len(key)
            ))

        super().__init__(key, number_of_params=1)
        self._aes: Cipher = None
        self._encryptor: CipherContext = None
        self._decryptor: CipherContext = None
        self._in_process: CipherProcess = CipherProcess.NONE

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if not isinstance(plaintext, bytes):
            raise HTypeError("plaintext", plaintext, bytes)

        if not self._key:
            raise KeyError("Please provide key before calling encrypt()")

        if self._aes is None:
            raise CipherParameterError("Please set nonce "
            "value before calling encrypt().")

        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.ENCRYPT
            self._encryptor = self._aes.encryptor()

        if self._in_process is not CipherProcess.ENCRYPT:
            raise ResetError("You are in {} process, please call reset() "
            "before calling encrypt().".format(self._in_process.name))

        ciphertext = self._encryptor.update(plaintext)

        if finalize:
            ciphertext += self.finalize()

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if not isinstance(ciphertext, bytes):
            raise HTypeError("ciphertext", ciphertext, bytes)

        if not self._key:
            raise KeyError("Please provide key before "
            "calling decrypt()")

        if self._aes is None:
            raise CipherParameterError("Please set nonce "
            "value before calling decrypt().")

        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.DECRYPT
            self._decryptor = self._aes.decryptor()

        if self._in_process is not CipherProcess.DECRYPT:
            raise ResetError("You are in {} process, please "
            "call reset() before calling decrypt()".format(self._in_process.name))
        
        plaintext = self._decryptor.update(ciphertext)
        
        if finalize:
            plaintext += self.finalize()

        return plaintext

    def finalize(self) -> bytes:
        if self._aes is None:
            raise CipherParameterError("Please set nonce value "
            "before calling finalize().")

        if self._in_process is CipherProcess.ENCRYPT:
            finaltext = self._encryptor.finalize()
            self._encryptor = None

        elif self._in_process is CipherProcess.DECRYPT:
            finaltext = self._decryptor.finalize()
            self._decryptor = None

        elif self._in_process is CipherProcess.FINALIZED:
            raise ResetError("Unknown process in your object "
            "({}).".format(self._in_process.name))
        else:
            raise SymmetricError("Unknown process ({}).".format(self._in_process.name))

        self._in_process = CipherProcess.FINALIZED
        return finaltext

    def set_param(self, index: int, param: bytes) -> None:
        if not isinstance(param, bytes):
            raise CipherParameterError("Parameters of AES must "
            "be a bytes object.")

        if index == 0:
            if len(param) * 8 != algorithms.AES.block_size:
                raise CipherParameterError("Invalid length of nonce "
                "value ({} bits), expected less than {} bits.".format(
                        len(param) * 8,
                        algorithms.AES.block_size
                ))

            self._nonce = param
            self._aes = Cipher(
                algorithms.AES(self._key),
                modes.CTR(self._nonce),
                default_backend()
            )
        else:
            raise CipherParameterError("AES only use the nonce "
            "value as its parameter.")

    def get_param(self, index) -> bytes:
        if index == 0:
            return self._nonce
        else:
            raise CipherParameterError("AES only use the nonce "
            "value as its parameter.")

    def reset(self, auto_renew_params: bool = True):
        if self._in_process not in (CipherProcess.NONE, CipherProcess.FINALIZED):
            raise FinalizeCipherError("Please finalize() the process "
            "before calling reset().")

        if auto_renew_params:
            new_nonce = os.urandom(algorithms.AES.block_size // 8)
        else:
            new_nonce = self._nonce

        self._encryptor = None
        self._decryptor = None
        self._in_process = CipherProcess.NONE
        self.set_param(0, new_nonce)


@CipherID.register
class AES_CBC(HKSCipher):
    def __init__(self, key: bytes):
        if not isinstance(key, bytes):
            raise HTypeError("key", key, bytes)

        if len(key) * 8 not in algorithms.AES.key_sizes:
            raise CipherParameterError("Key size of AES must be "
            "in {} (bits), not {} (bytes).".format(
                set(algorithms.AES.key_sizes),
                len(key)
            ))
        super().__init__(key, number_of_params=1)
        self._aes = None
        self._encryptor = None
        self._decryptor = None

        self._in_process = CipherProcess.NONE

        self._pkcs7 = padding.PKCS7(128)
        self._padder = None
        self._unpadder = None

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if not isinstance(plaintext, bytes):
            raise HTypeError("plaintext", plaintext, bytes)

        if not self._key:
            raise KeyError("Please provide key before calling encrypt()")

        if self._aes is None:
            raise CipherParameterError("Please set iv value "
            "before calling encrypt().")

        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.ENCRYPT
            self._encryptor = self._aes.encryptor()
            self._padder = self._pkcs7.padder()

        if self._in_process is not CipherProcess.ENCRYPT:
            raise ResetError("You are in {} process, please call reset() "
            "before calling decrypt().".format(self._in_process.name))

        text = self._padder.update(plaintext)
        ciphertext = self._encryptor.update(text)
        
        if finalize:
            ciphertext += self.finalize()

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if not isinstance(ciphertext, bytes):
            raise HTypeError("ciphertext", ciphertext, bytes)

        if not self._key:
            raise KeyError("Please provide key before calling decrypt()")

        if self._aes is None:
            raise CipherParameterError("Please set iv value "
            "before calling decrypt().")

        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.DECRYPT
            self._decryptor = self._aes.decryptor()
            self._unpadder = self._pkcs7.unpadder()

        if self._in_process is not CipherProcess.DECRYPT:
            raise ResetError("You are in {} process, please call reset() "
            "before calling decrypt().".format(self._in_process.name))

        padded_text = self._decryptor.update(ciphertext)
        plaintext = self._unpadder.update(padded_text)

        if finalize:
            plaintext += self.finalize()

        return plaintext

    def finalize(self) -> bytes:
        if self._aes is None:
            raise FinalizeCipherError("Please set nonce value "
            "before calling finalize().")

        if self._in_process is CipherProcess.ENCRYPT:
            text = self._padder.finalize()
            finaltext = self._encryptor.update(text)
            finaltext += self._encryptor.finalize()

            self._encryptor = None
            self._padder = None

        elif self._in_process is CipherProcess.DECRYPT:
            padded_text = self._decryptor.finalize()
            finaltext = self._unpadder.update(padded_text)
            finaltext += self._unpadder.finalize()

            self._decryptor = None
            self._unpadder = None

        elif self._in_process is CipherProcess.FINALIZED:
            raise ResetError("Unknown process in your object "
            "({}).".format(self._in_process.name))
        else:
            raise SymmetricError("Unknown process ({}).".format(self._in_process.name))

        self._in_process = CipherProcess.FINALIZED
        return finaltext

    def set_param(self, index: int, param: bytes) -> None:
        if not isinstance(param, bytes):
            raise CipherParameterError("Parameters of AES "
            "must be a bytes object.")

        if index == 0:
            if len(param) * 8 != algorithms.AES.block_size:
                raise CipherParameterError("Invalid length of "
                "IV value ({} bits), expected {} bits.".format(
                        len(param) * 8,
                        algorithms.AES.block_size
                    )
                )

            self._iv = param
            self._aes = Cipher(
                algorithms.AES(self._key),
                modes.CBC(self._iv),
                default_backend()
            )
        else:
            raise CipherParameterError("AES CBC only use the "
            "IV value as its parameter.")

    def get_param(self, index) -> bytes:
        if index == 0:
            return self._iv
        else:
            raise CipherParameterError("AES CBC only use the "
            "IV value as its parameter.")

    def reset(self, auto_renew_params: bool = True):
        if self._in_process not in (CipherProcess.NONE, CipherProcess.FINALIZED):
            raise FinalizeCipherError("Please finalize() the "
            "process before calling reset().")

        if auto_renew_params:
            new_iv = os.urandom(16)
        else:
            new_iv = self._iv
        
        self._encryptor = None
        self._decryptor = None
        self._padder = None
        self._unpadder = None
        self._in_process = CipherProcess.NONE
        self.set_param(0, new_iv)


@CipherID.register
class HybridCipher(HKSCipher):
    def __init__(self, cipher_obj: HKSCipher, hash_obj: HKSHash = SHA256()):
        super().__init__(None, cipher_obj._number_of_params)
        self._cipher = cipher_obj
        self._hash = hash_obj

        self._in_process = CipherProcess.NONE

        self._stored_digest = None

    def encrypt(self, plaintext: bytes, finalize=True) -> bytes:
        if not isinstance(plaintext, bytes):
            raise HTypeError("plaintext", plaintext, bytes)

        # ciphertext = E(plaintext + hash(plaintext))
        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.ENCRYPT

        if self._in_process is not CipherProcess.ENCRYPT:
            raise Exception("You are in {} process, please call reset() "
            "before calling encrypt()".format(self._in_process.name))

        self._hash.update(plaintext)
        ciphertext = self._cipher.encrypt(plaintext, finalize=False)

        if finalize:
            ciphertext += self.finalize()

        return ciphertext

    def decrypt(self, ciphertext: bytes, finalize=True) -> bytes:
        if not isinstance(ciphertext, bytes):
            raise HTypeError("ciphertext", ciphertext, bytes)

        if self._in_process is CipherProcess.NONE:
            self._in_process = CipherProcess.DECRYPT
            self._stored_digest = b""

        if self._in_process is not CipherProcess.DECRYPT:
            raise ResetError("You are in {} process, please call reset() "
            "before calling decrypt()".format(self._in_process.name))
        
        plaintext = self._cipher.decrypt(ciphertext, finalize=False)

        all_plaintext = self._stored_digest + plaintext

        actual_plaintext = all_plaintext[ : -self._hash.digest_size]

        self._stored_digest = all_plaintext[-self._hash.digest_size : ]

        self._hash.update(actual_plaintext)

        if finalize:
            actual_plaintext += self.finalize()

        return actual_plaintext

    def finalize(self) -> bytes:
        if self._in_process is CipherProcess.ENCRYPT:
            msg_digest = self._hash.finalize()
            finaltext = self._cipher.encrypt(msg_digest, finalize=True)
            return finaltext

        elif self._in_process is CipherProcess.DECRYPT:
            plaintext = self._cipher.finalize()
            all_plaintext = self._stored_digest + plaintext

            finaltext = all_plaintext[:-self._hash.digest_size]

            self._stored_digest = all_plaintext[-self._hash.digest_size:]

            self._hash.update(finaltext)
            
            expected_digest = self._stored_digest
            computed_digest = self._hash.finalize()

            if expected_digest != computed_digest:
                raise UnAuthenticatedPacketError("Packet authentication fails.")

            self._stored_digest = None
        
        elif self._in_process is CipherProcess.FINALIZED:
            raise ResetError("Unknown process in your object "
            "({}).".format(self._in_process.name))
        else:
            raise SymmetricError("Unknown process ({}).".format(self._in_process.name))
        
            
        self._in_process = CipherProcess.FINALIZED
        return finaltext

    def set_param(self, index: int, param: bytes) -> None:
        return self._cipher.set_param(index, param)

    def get_param(self, index: int) -> bytes:
        return self._cipher.get_param(index)

    def reset(self, auto_renew_params: bool = True):
        self._hash.reset()
        self._cipher.reset(auto_renew_params)
        self._stored_digest = None
        self._in_process = CipherProcess.NONE
