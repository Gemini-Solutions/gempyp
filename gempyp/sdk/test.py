from gempyp.sdk.test_1 import test_new_meth
from gempyp.sdk.test_1 import test_old_meth
import traceback


try:
    test_new_meth()
    test_old_meth()
except Exception as e:
    traceback.print_exc()