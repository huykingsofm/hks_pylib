from hks_pylib.logger import StandardLoggerGenerator


def test_logger():
    standard_logger_generator = StandardLoggerGenerator("logger.log")
    log = standard_logger_generator.generate("Name", {"user": ["info"], "dev": ["ALL"]})
    log("user", "info", "hks_pylib")
    log("dev", "debug", "huykingsofm")
