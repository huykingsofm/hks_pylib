# hks_pylib
A Python 3 utility library of [huykingsofm](https://github.com/huykingsofm). It has some modules, including:
- `logger`: A module is used to print notifications to the console screen or write logs to file. It is special because you can disable the print/write statement by modifying a few parameters without commenting or deleting them manually. 
- `cryptography`: A wrapper crypto module bases on and is followed by the implementation style of [cryptography](https://pypi.org/project/cryptography/). It is easier to use than the original one and fits many functions in our projects.
- `done`: A module defines a class (`Done`) for returning complex values more conveniently.
- `http`: A module is used to parse or generate raw HTTP packets.
- `math`: A module implements some no-builtin mathematic operations.

# How to build
Our library is only supported by Python>=3.7.1. Now we test it only on Python 3.7.1. If you meet any problems, even if with other versions, you could [create an issue](https://github.com/huykingsofm/hks_pylib/issues) to notify us. We will solve them as quickly as possible.  

## Create Virtual Environment (optional but IMPORTANT)
*If you had your virtual environment, you can ignore this step.* 

You ought to create a virtual environment to avoid conflicting with other applications on your machine when installing our module. The virtual environment must be installed with [Python 3](https://www.python.org/downloads).  
I highly recommend you to use [Anaconda](https://www.anaconda.com/products/individual) because of its utilities. The command of creating a virtual environment in Anaconda is:
```bash
$ conda create -n your_venv_name python=3.7.1
$ conda activate your_venv_name
(your_venv_name) $ _ 
```

Or use `Python venv`:
```bash
$ python -m venv path/to/your/venv
$ path/to/your/venv/Scripts/activate.bat
(your_venv_name) $ _
```

## Method 1: Install the stablest PyPI version
```bash
(your_venv_name) $ pip install hks_pylib
```

## Method 2: Install the newest version

```bash
(your_venv_name) $ git clone https://github.com/huykingsofm/hks_pylib.git
(your_venv_name) $ cd hks_pylib
(your_venv_name) hks_pylib $ pip install -e .
```

# How to use
Just use `import` statement and enjoy it. We will write documentation and tutorials as soon as possible so that you can understand our library easier.

```python
# A Done object can be used to substitute 
# complex return values
from hks_pylib.done import Done

# A class is used to print/write 
# logs to console/file
from hks_pylib.logger import StandardLogger  

# A class is used to generate StandardLogger objects.
# You should use this class instead of 
# using StandardLogger directly
from hks_pylib.logger import StandardLoggerGenerator  

# Some common ciphers
from hks_pylib.cipher import NoCipher, AES_CBC, SimpleSSL 

# You can parse or generate raw HTTP packets with these class
from hks_pylib.http import HTTPParser, HTTPGenerator  
```
