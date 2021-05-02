import threading
from hks_pylib.logger.logger_generator import StandardLoggerGenerator
from hks_pylib.logger.logger import Display, console_output
from hks_pylib.logger.standard import StdLevels, StdUsers


def test_logger():
    standard_logger_generator = StandardLoggerGenerator("tests/test_logger.log")
    log = standard_logger_generator.generate(
        "Name", {StdUsers.USER: [StdLevels.INFO], StdUsers.DEV: Display.ALL})
    log(StdUsers.USER, StdLevels.INFO, "hks_pylib")
    log(StdUsers.DEV, StdLevels.DEBUG, "huykingsofm")


if __name__ == "__main__":
    test_logger()