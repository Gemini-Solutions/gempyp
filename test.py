from gempyp.sdk.executor import Executor
from gempyp.libs.enums.status import status
import pytest

@pytest.mark.webtest
def test_new_meth():
    obj = Executor()
    assert 4+1==5
    obj.reporter.addRow("Assertion", "Status of assertion", status.PASS)

def test_old_meth_1():
    obj2 = Executor()
    print("ABC")
    assert 8+1 == 9
    print("DEF")
    obj2.reporter.addRow("Assertion", "Status of assertion", status.FAIL)

# if __name__ == "__main__":
#     try:
#         new_meth()
#         old_meth_1()
#     except Exception as e:
#         traceback.print_exc()