import threading
from hks_pylib.logger.logger_generator import StandardLoggerGenerator
from hks_pylib.logger.logger import Display, console_output

def console_thread(id):
    for i in range(20):
        console_output.write(id, "hks_pylib", auto_avoid_conflicting=True)

def test_console_conflicting():
    threading.Thread(target=console_thread, args=(1, )).start()
    threading.Thread(target=console_thread, args=(2, )).start()

def test_logger():
    standard_logger_generator = StandardLoggerGenerator("tests/test_logger.log")
    log = standard_logger_generator.generate("Name", {"user": ["info"], "dev": Display.ALL})
    log("user", "info", "hks_pylib")
    log("dev", "debug", "huykingsofm")


if __name__ == "__main__":
    test_logger()