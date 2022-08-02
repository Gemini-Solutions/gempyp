import traceback
from gempyp.sdk.executor import Executor
from gempyp.libs.enums.status import status


def new_meth():
    obj = Executor()
    obj.reporter.addRow("test", "test", status.PASS)
    obj.reporter.addRow("test_1", "test", status.PASS)

def old_meth():
    obj2 = Executor()
    obj2.reporter.addRow("test", "test_2", status.PASS)
    obj2.reporter.addRow("test", "test_2", status.PASS)

if __name__ == "__main__":
    try:
        new_meth()
        old_meth()
    except Exception as e:
        traceback.print_exc()