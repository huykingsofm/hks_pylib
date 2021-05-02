from hks_pylib.hksenum import HKSEnum


class Users(HKSEnum):
    "Extending this enum class to define Users in Logger."


class Levels(str, HKSEnum):
    "Extending this enum class to define Levels in Logger."


class StdUsers(Users):
    DEV = "dev"
    USER = "user"


class StdLevels(Levels):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    DEBUG = "debug"
    BENCHMARK = "benchmark"
