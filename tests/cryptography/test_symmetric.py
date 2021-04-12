import os
import random
from cryptography.hazmat.primitives import ciphers
import pytest

from cryptography.hazmat.primitives.ciphers.algorithms import AES

from hks_pylib import math
from hks_pylib.cryptography._cipher import HKSCipher
from hks_pylib.cryptography.symmetrics import XorCipher, NoCipher, AES_CBC, AES_CTR, HybridCipher


AES_KEY = b"0123456789abcdeffedcba9876543210"
PLAIN_TEXT = b"huykingsofm"


@pytest.fixture
def aes_key():
    return AES_KEY


@pytest.fixture
def plaintext():
    return PLAIN_TEXT


@pytest.fixture
def cipher():
    return NoCipher()


def run_cipher(cipher: HKSCipher, plaintext):
    cipher.reset()
    allciphertext = []
    allplaintext = b""
    for i in range(1000):
        allciphertext.append(cipher.encrypt(plaintext, False))
        allplaintext += plaintext
    allciphertext.append(cipher.finalize())
    
    for i in range(cipher._number_of_params):
        param = cipher.get_param(i)
        cipher.set_param(i, param)

    cipher.reset(False)

    all_computed_plaintext = b""
    for ciphertext in allciphertext:
        all_computed_plaintext += cipher.decrypt(ciphertext, finalize=False)
    all_computed_plaintext += cipher.finalize()

    assert all_computed_plaintext == allplaintext

@pytest.mark.parametrize(
    'cipher',
    [
        NoCipher(),
        XorCipher(os.urandom(100000)),
        AES_CBC(AES_KEY),
        AES_CTR(AES_KEY),
        HybridCipher(AES_CBC(AES_KEY))
    ]
)
def test_cipher(benchmark, cipher, plaintext):
    plaintext = os.urandom(1000)
    benchmark.pedantic(run_cipher, args=(cipher, plaintext), rounds=5)

def test_SIMP():
    length_of_message = random.randint(1000, 2000)
    A = os.urandom(length_of_message)
    B = os.urandom(length_of_message)
    C = os.urandom(length_of_message)
    keysize = random.choice([16, 24, 32])
    print("keysize:", keysize)
    K1 = os.urandom(keysize)
    K2 = os.urandom(keysize)
    K3 = os.urandom(keysize)
    NONCE1 = os.urandom(AES.block_size // 8)
    NONCE2 = os.urandom(AES.block_size // 8)
    NONCE3 = os.urandom(AES.block_size // 8)

    #print("Expected:", Math.xor_bytes(A, B))

    E1 = AES_CTR(key=K1)
    E1.set_param(0, NONCE1)
    EA1 = E1.encrypt(A)
    E1.reset(False)
    #print("S received EA1:", EA1)

    E2 = AES_CTR(key=K2)
    E2.set_param(0, NONCE2)
    EB2 = E2.encrypt(B)
    E2.reset(False)
    #print("S received EB2:", EB2)

    EAB12 = math.bxor(EA1, EB2)
    #print("S calculate EAB12:", EAB12)

    E3 = AES_CTR(K3)

    E3.set_param(0, NONCE3)
    E1.set_param(0, NONCE1)
    EC13 = E3.encrypt(E1.encrypt(C))
    E1.reset(False)
    E3.reset(False)
    #print("P1 calculate EC13:", EC13)

    E3.set_param(0, NONCE3)
    E2.set_param(0, NONCE2)
    EC23 = E3.encrypt(E2.encrypt(C))
    E2.reset(False)
    E3.reset(False)
    #print("P2 calculate EC23", EC23)

    K1K2 = math.bxor(EC13, EC23)
    #print("S calculate K1K2:", K1K2)

    AB = math.bxor(EAB12, K1K2)
    #print("S recover AB:", AB)
    assert AB == math.bxor(A, B)


if __name__ == "__main__":
    run_cipher(AES_CBC(AES_KEY), PLAIN_TEXT)
