# hks_lib
This is huykingsofm's python library, including:
- `logger`: A module is used to print notifications to console screen or write logs to file. It is special because you can disable the print/write statement by modifying few parameters without having to delete or comment them. 
- `cipher`: A very simple crypto module bases on [cryptography](https://pypi.org/project/cryptography/). It is easier to use than original one.
- `done`: A module defines a class (`Done`) for returning complexity values easier.
- `http`: A module is used to read and generate raw http packets.

# How to build
We are assuming that your code is running on the Python 3.7.1. If you meet any problems, even if with other versions, let [create an issue](https://github.com/huykingsofm/hks_pylib/issues) to notify us. We will solve them as quick as possible.  

## Create Virtual Enviroment (optional but IMPORTANT)
*If you had your own virtual enviroment, you can ignore this step.* 

You should create a virtual enviroment to avoid conflicting with other applications on your machine when installing our module. The virtual enviroment should be installed with [Python 3.7.1](https://www.python.org/downloads/release/python-371/) (you can use other Python versions but we can't ensure that unexpected errors will not appear suddenly).  
I highly recommend you to use [Anaconda](https://www.anaconda.com/products/individual) because its utilities. The command of creating virtual enviroment in Anaconda is:
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

## Method 1: Install the most stable version
```bash
(your_venv_name) $ pip install hks_pylib
```

## Method 2: Install the newest version

```bash
(your_venv_name) $ pip install -r requirements.txt
(your_venv_name) $ pip install -e .
```

# How to use
Just use `import` statement and enjoy it. We will write documentations and tutorials as soon as possible so that you can understand our library easier.

```python
# A Done object can be used to substitute 
# complexity return value
from hks_pylib.done import Done

# A class is used to print/write 
# logs console/file
from hks_pylib.logger import StandardLogger  

# A class is used to generate StandardLogger objects.
# You should use this class instead of 
# using StandardLogger directly
from hks_pylib.logger import StandardLoggerGenerator  

# Some common ciphers
from hks_pylib.cipher import NoCipher, AES_CBC, SimpleSSL 

# You can create or read raw http packets with these class
from hks_pylib.http import HTTPReader, HTTPWriter  
```
