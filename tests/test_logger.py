from hks_pylib.logger.logger_generator import StandardLoggerGenerator
from hks_pylib.logger.logger import Display

def test_logger():
    standard_logger_generator = StandardLoggerGenerator("tests/test_logger.log")
    log = standard_logger_generator.generate("Name", {"user": ["info"], "dev": Display.ALL})
    log("user", "info", "hks_pylib")
    log("dev", "debug", "huykingsofm")


if __name__ == "__main__":
    test_logger()