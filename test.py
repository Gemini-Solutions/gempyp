import traceback
from gempyp.sdk.executor import Executor
from gempyp.libs.enums.status import status
import pytest


def test_new_meth():
    obj = Executor()
    obj.reporter.addRow("test", "test", status.PASS)

def test_old_meth_1():
    obj2 = Executor()
    obj2.reporter.addRow("test2111", "test_2", status.PASS)
    obj2.reporter.addRow("test1", "test_2", status.PASS)

# if __name__ == "__main__":
#     try:
#         new_meth()
#         old_meth_1()
#     except Exception as e:
#         traceback.print_exc()