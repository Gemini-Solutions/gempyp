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

def test_old_meth():
    obj2 = Executor()
    obj2.reporter.addRow("test_3", "test_3", status.PASS)
    obj2.reporter.addRow("test", "test_2", status.PASS)

def test_new_meth():
    obj2 = Executor()
    obj2.reporter.addRow("test_4", "test_4", status.PASS)
    obj2.reporter.addRow("test", "test_2", status.PASS)

if __name__ == "__main__":
    try:
        new_meth()
        old_meth()
        test_new_meth()
        test_old_meth()

    except Exception as e:
        traceback.print_exc()