import threading
from hks_pylib.logger.logger_generator import InvisibleLoggerGenerator, StandardLoggerGenerator
from hks_pylib.logger.logger import Display, console_output
from hks_pylib.logger.standard import StdLevels, StdUsers
from hks_pylib.logger import acprint


def test_logger():
    invisible_logger_generator = InvisibleLoggerGenerator()
    standard_logger_generator = StandardLoggerGenerator("tests/test_logger.log")
    log = invisible_logger_generator.generate(
        "Name", {StdUsers.USER: [StdLevels.INFO], StdUsers.DEV: Display.ALL})
    log(StdUsers.USER, StdLevels.INFO, "hks_pylib")
    log(StdUsers.DEV, StdLevels.DEBUG, "huykingsofm")

    log = standard_logger_generator.generate(
        "Name", {StdUsers.USER: [StdLevels.INFO], StdUsers.DEV: Display.ALL})
    log(StdUsers.USER, StdLevels.INFO, "hks_pylib")
    log(StdUsers.DEV, StdLevels.DEBUG, "huykingsofm")

    acprint("huythongminh", end="\n")

if __name__ == "__main__":
    test_logger()