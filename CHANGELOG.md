# Change log
## Version 0.0.5
+ Change allmost all general exceptions to our exceptions (in `hks_pylib.errors` module).
+ Add the `Output` class to `hks_pylib.logger.config`. Now logger can avoid writing into conflict.
+ Add a wrapper module `hks_pylib.hksenum` of builtin python `enum`.
+ Change many constants to `HKSEnum` type.
+ Divide module `ciphers` into multiple submodules and move them to folder `ciphers/`.
+ Divide module `logger` into multiple submodules and move them to folder `logger/`.
+ Remove `requirements.txt`.
+ Add `Bitwise` operator to `math`.
+ Add `batchcrypt` module to `cryptography`.