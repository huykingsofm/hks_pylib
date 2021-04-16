"""
hks_pylib
==============

A Python 3 utility library of [huykingsofm](https://github.com/huykingsofm).
It has some modules, including:
- `logger`: A module is used to print notifications to the console screen
or write logs to file. It is special because you can disable the
print/write statement by modifying a few parameters without commenting or
deleting them manually.
- `cryptography`: A very simple crypto module is based on
[Crypto](https://pypi.org/project/pycrypto/) and followed by the implement
style of [cryptography](https://pypi.org/project/cryptography/). It is
easier to use than the original ones and fits some functions in our
projects. All classes in this module have the same methods.
- `done`: A module defines a class (`Done`) for returning complex values
more conveniently.
- `http`: A module is used to parse or generate raw HTTP packets.
"""

from hks_pylib.version import __version__
