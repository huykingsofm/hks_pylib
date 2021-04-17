"""
hks_pylib
==============
A Python 3 utility library of [huykingsofm](https://github.com/huykingsofm). 
It has some modules, including:
- `logger`: A module is used to print notifications to the console screen 
or write logs to file. It is special because you can disable the print/write 
statement by modifying a few parameters without commenting or deleting them manually. 
- `cryptography`: A wrapper crypto module bases on and is followed by the 
implementation style of [cryptography](https://pypi.org/project/cryptography/). 
It is easier to use than the original one and fits many functions in our projects.
- `done`: A module defines a class (`Done`) for returning complex values 
more conveniently.
- `http`: A module is used to parse or generate raw HTTP packets.
- `math`: A module implements some no-builtin mathematic operations.
- `hksenum`: A wrapper module of `Enum` is more convenient than the original.
"""

from hks_pylib.version import __version__
