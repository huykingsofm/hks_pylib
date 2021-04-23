# Change log
## Version 0.0.5
+ Change allmost all generic exceptions to high identified exceptions (in modules of `hks_pylib.errors`).
+ Add the `Output` class to `hks_pylib.logger.config`. Now logger can easily avoid conflicting in printing.
+ Add a wrapper module `hks_pylib.hksenum` of builtin python class `Enum`. Change many constants to `HKSEnum` type.
+ Divide module `ciphers` into multiple submodules and move them to folder `ciphers/`.
+ Divide module `logger` into multiple submodules and move them to folder `logger/`.
+ Remove `requirements.txt`.
+ Add `Bitwise` operator to `math`.
+ Add [`batchcrypt`](https://www.usenix.org/conference/atc20/presentation/zhang-chengliang) module to `hks_pylib.cryptography`.
+ Add an example of `batchcrypt` in folder `examples/`.