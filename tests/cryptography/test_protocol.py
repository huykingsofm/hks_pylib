from hks_pylib.cryptography.protocols import DiffieHellmanExchange

def test_DHE():
    P1 = DiffieHellmanExchange()
    P2 = DiffieHellmanExchange()

    pk1 = P1.public_key
    pk2 = P2.public_key

    sk1 = P1.exchange(pk2)
    sk2 = P2.exchange(pk1)

    sk1 = P1.derive_key(sk1, 32)
    sk2 = P2.derive_key(sk2, 32)

    assert sk1 == sk2