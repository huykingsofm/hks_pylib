from hks_pylib.logger import StandardLoggerGenerator

def test_logger():
    standard_logger_generator = StandardLoggerGenerator("logger.log")
    log = standard_logger_generator.generate("Name", {"user": ["info"], "dev": ["debug"]})
    log("user", "info", "huythongminh")
    log("dev", "debug", "huyaaa")