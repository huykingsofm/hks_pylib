"""
hks_pylib
==============

This is a Python 3 utility library of `huykingsofm` (https://github.com/huykingsofm).
It has some modules, including:
- `logger`: A module is used to print notifications to the 
console screen or write logs to file. It is special because 
you can disable the print/write statement by modifying few
parameters without having to delete or comment them manually. 
- `cipher`: A very simple crypto module based on
`cryptography` (https://pypi.org/project/cryptography/).
It is easier to use than the original one.
- `done`: A module defines a class (`Done`) for returning
complex values more conveniently.
- `http`: A module is used to parse or generate raw http
packets.
"""

import hks_pylib.cipher as _cipher
from hks_pylib.version import __version__

_cipher.AllCipher.register(_cipher.NoCipher)
_cipher.AllCipher.register(_cipher.XorCipher)
_cipher.AllCipher.register(_cipher.AES_CBC)
_cipher.AllCipher.register(_cipher.AES_CTR)
_cipher.AllCipher.register(_cipher.SimpleSSL)
