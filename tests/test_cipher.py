import pytest
from hks_pylib.cipher import XorCipher, NoCipher, AES_CBC, AES_CTR, SimpleSSL

AES_KEY = b"0123456789abcdef"
PLAIN_TEXT = b"huykingsofm"

@pytest.fixture
def plaintext():
    return PLAIN_TEXT

@pytest.mark.parametrize('cipher', [NoCipher(), XorCipher(b"1"), AES_CBC(AES_KEY), AES_CTR(AES_KEY), SimpleSSL(AES_CTR(AES_KEY))])
def test_cipher(cipher, plaintext):
    cipher.reset_params()
    ciphertext = cipher.encrypt(plaintext)
    assert cipher.decrypt(ciphertext) == plaintext
