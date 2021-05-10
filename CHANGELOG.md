# Change log
## Version 0.0.7
+ Fix the error of `InvisibleLogger`.
+ Fix `reset()` in `AES_CTR` and `AES_CBC`.
+ Fix `save...()` and `load...()` in `RSAKey`.
+ Add the `acprint(.)` for avoid conflicting print.
+ Add `@as_object` decorator.
+ Add `MD5` to `hashes`.
+ Add `KeyGenerator` to `ciphers`.


## Version 0.0.6
+ Change .gitignore to template of Python.
+ Change the `http` style.
+ Change the `logger` to `HKSEnum` style.
+ Add `InvisibleLoggerGenerator`, `InvisibleLogger` for more convenient.
+ Add some utility methods to `HKSEnum` and `Done`.
+ Change many error types and replace some errors to `hkserror`.
<!---Commit at 02/05/2021 8:00:00-->

## Version 0.0.5
+ Change allmost all generic exceptions to highly identified exceptions (in modules of `hks_pylib.errors`).
+ Add the `Output` class to `hks_pylib.logger.config`. Now logger can easily avoid conflicting in printing.
+ Add a wrapper module `hks_pylib.hksenum` of builtin python class `Enum`. Change many constants to `HKSEnum` type.
+ Divide module `hks_pylib.cryptography.ciphers` into multiple submodules and move them to folder `cryptography/ciphers/`.
+ Divide module `hks_pylib.logger` into multiple submodules and move them to folder `logger/`.
+ Remove `requirements.txt`.
+ Add `Bitwise` operator to `math`.
+ Add [`batchcrypt`](https://www.usenix.org/conference/atc20/presentation/zhang-chengliang) module to `hks_pylib.cryptography`.
+ Add an example of `batchcrypt` in folder `examples/`.