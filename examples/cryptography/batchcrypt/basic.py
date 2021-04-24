import time
import random

from hks_pylib.cryptography.batchcrypt.batchnumber import SignedBatchNumber
from hks_pylib.errors.cryptography.batchcrypt.quantization import OverflowQuantizerError
from hks_pylib.errors.cryptography.batchcrypt.integer import OverflowIntegerError


SLEEP_TIME = 0


def random_array(low, high, num):
    # Random a float array of num elements, whose elements is in [low, high]
    random_float = lambda l, h: random.randint(int(l * 1000), int(h * 1000)) / 1000
    return [random_float(low, high) for _ in range(num)]

def encrypt(plaintext):
    # Please implement this function as your demand.
    # It must be an additively homomorphic encryption (such as pailier).
    return plaintext


def decrypt(ciphertext):
    # Please implement this function as your demand.
    # It must be an additively homomorphic decryption (such as pailier).
    return ciphertext


def add(ciphertext1, ciphertext2):
    # It should be implement this function for the addition operation of
    # an additively homomorphic cipher.
    return ciphertext1 + ciphertext2


def communication():
    # There are three parties in this example:
    #   + The Server.
    #   + The Client 1 (host client).
    #   + The Client 2.

    # Context: The Client 1 and 2 request the Server to compute sum of two
    #   array A and B. However, the condition is the Server must not see 
    #   the original array.

    # Method: 
    #   + Client 1 generate a additively HE keypair, called K = (puk, prk).
    #   + Client 1 shares puk with Client 2.
    #   + Client 1 encrypts A by puk, create A'.
    #   + Client 2 encrypts B by puk, create B'. 
    #   + Client 1 and 2 send A', B' to the Server.
    #   + The Server perform additive operation on these encrypted array.
    #   + The Server send the result to Client 1.
    #   + Client 1 decrypts the result by prk.

    # BatchNumber:
    #   + A and B have many elements, so that the ciphertext size is very large.
    #   + Before encrypting arrays, A and B will be batched by
    #       a class called SignedBatchNumber.
    #   + Encryption and decryption perform on these batched data.

    # --> THE COMMON CONSTANTS BETWEEN THE SERVER AND CLIENTS <--

    frange = (-20.0, 20.0)  # Range of float value in quantization.
                            # It should be cover addition and subtraction operations.
                            # Example: In this case (frange = -20, 20), the result of
                            # your addition operation shouldn't exceed this range.
                            # Otherwise, an error OverflowIntegerError 
                            # or OverflowQuantizerError will occur.  

    isize = 32  # Size of int value in quantization.
                # The larger size, the smaller loss.

    max_numbers_per_batch = 10  # == len(A) == len(B)
                                # If an array is not enough numbers, 
                                # you should perform a padding operation.

    epsilon = 1e-5  # Expected minimum different of float 
                    # value between before and after quantizing.
    # ---------------------------------------------------

    # SignedBatchNumber.quantizer should be initialized the same at every entities.
    # At the client 1, client 2, and server.
    SignedBatchNumber.quantizer(
        float_range=frange,
        int_size=isize
    )
    print("[0] The server initialized the quantizer with common constants.")
    print("[1] The client 1 initialized the quantizer with common constants.")
    print("[2] The client 2 initialized the quantizer with common constants.")
    time.sleep(SLEEP_TIME)
    print()

    # AT THE CLIENT 1 (HOST CLIENT)
    A = random_array(frange[0] + 10, frange[1] - 10, max_numbers_per_batch)
    print("[1] The client 1 created the array A.")
    print("[1] A =", A)
    time.sleep(SLEEP_TIME)
    print()

    batchA = SignedBatchNumber.bind(*A, size=isize)
    raw_batchA = batchA.raw()
    print("[1] The client 1 binded A to batchA.")
    print("[1] batchA =", batchA.raw())
    time.sleep(SLEEP_TIME)
    print()

    encrypted_batchA = encrypt(raw_batchA)
    print("[1] The client 1 encrypted batchA with a homomorphic encryption.")
    print("[1] encrypted_batchA =", encrypted_batchA)
    time.sleep(SLEEP_TIME)
    print()
    # --> Send encrypted_batchA to the Server.
    print("[1] The client 1 sends the encrypted_batchA to the server.")
    time.sleep(SLEEP_TIME)
    print()


    # AT THE CLIENT 2
    B = random_array(frange[0] + 10, frange[1] - 10, max_numbers_per_batch)
    print("[2] The client 2 created the array B.")
    print("[2] B =", B)
    time.sleep(SLEEP_TIME)
    print()

    batchB = SignedBatchNumber.bind(*B, size=isize)
    raw_batchB = batchB.raw()
    print("[2] The client 2 binded B to batchB.")
    print("[2] batchB =", batchB.raw())
    time.sleep(SLEEP_TIME)
    print()

    encrypted_batchB = encrypt(raw_batchB)
    print("[2] The client 2 encrypted batchB with a homomorphic encryption.")
    print("[2] encrypted_batchB =", encrypted_batchB)
    time.sleep(SLEEP_TIME)
    print()
    # --> Send encrypted_batchB to the Server.
    print("[2] The client 2 sends the encrypted_batchB to the server.")
    time.sleep(SLEEP_TIME)
    print()

    # AT THE SERVER
    # It receives the encrypted_batchA and encrypted_batchB.
    print("[0] The server receives the encrypted_batchA from client 1.")
    print("[0] The server receives the encrypted_batchB from client 2.")
    time.sleep(SLEEP_TIME)
    print()

    # This is the addition opearation of homomorphic cipher.
    encrypted_batchR = add(encrypted_batchA, encrypted_batchB)
    print("[0] The server performs encrypted_batchA + encrypted_batchB "
    "under an additively homomorphic cipher context.")
    print("[0] encrypted_batchR =", encrypted_batchR)
    time.sleep(SLEEP_TIME)
    print()

    # --> Send encrypted_batchR to the host client (client 1).
    print("[0] The server sends the result of addition "
    "to the host client (client 1).")
    time.sleep(SLEEP_TIME)
    print()

    # AT CLIENT 1
    # It receives the encrypted_batchR and be expected to decrypt this batch
    print("[1] The host client (client 1) receives the encrypted_batchR from the server.")
    time.sleep(SLEEP_TIME)
    print()

    raw_batchR = decrypt(encrypted_batchR)
    print("[1] The host client (client 1) decrypts the encrypted_batchR to raw_batchR.")
    print("[1] raw_batchR =", raw_batchR)
    time.sleep(SLEEP_TIME)
    print()

    recover_batchR = SignedBatchNumber(
        batch=raw_batchR,
        num=max_numbers_per_batch,
        size=isize
    )
    print("[1] The host client (client 1) recovers batchR from raw_batchR.")
    time.sleep(SLEEP_TIME)
    print()

    print("[1] Check the accuracy and differentation of batchnumber.")
    print("[1] The number of elements of batchR:", len(recover_batchR))
    for i, (a, b) in enumerate(zip(A, B)):
        try:
            r = recover_batchR[i]

            if r < frange[0] or r > frange[1]:
                print("a={}, b={}, r={}".format(a, b, r))
                print(A, B)
                assert False
            assert abs(a + b - r) <= epsilon
        except OverflowQuantizerError:
            if frange[0] <= a + b and a + b <= frange[1]:
                print("a={}, b={}, r={}".format(a, b, r))
                print(A, B)
                assert False

if __name__ == "__main__":
    communication()