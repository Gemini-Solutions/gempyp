import enum


# IMP higher priority status must come above the lower priority in enum
# because the final status in report is based on the priority of the status
class status(enum.Enum):
    ERR = ("ERR",)
    FAIL = ("FAIL",)
    WARN = ("WARN",)
    PASS = ("PASS",)
    INFO = ("INFO",)
    EXE = "EXE"
