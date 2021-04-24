import os
from hks_pylib.cryptography.ciphers.asymmetrics import RSACipher, RSAKey


def run_RSA():
    blocksize = 1024  # 1KB
    nblocks = 1000
    keysize = 1024
    
    owner_rsakey = RSAKey()
    owner_rsakey.generate(keysize)
    owner = RSACipher(owner_rsakey)

    rsa_puk_bytes = owner_rsakey.serialize_public_key()
    other_rsakey = RSAKey()
    other_rsakey.deserialize_public_key(rsa_puk_bytes)
    other = RSACipher(other_rsakey)

    m = b""
    all_msg = b""
    for i in range(nblocks):
        msg = os.urandom(blocksize)
        all_msg += msg
        c = other.encrypt(msg, finalize=False)
        m += owner.decrypt(c, finalize=False)
    c = other.encrypt(b"")
    m += owner.decrypt(c)
    assert m == all_msg

def test_RSA(benchmark):
    benchmark.pedantic(run_RSA, rounds=5)