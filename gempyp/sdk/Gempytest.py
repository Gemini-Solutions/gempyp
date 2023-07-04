from gempyp.sdk.executor import Executor
from gempyp.libs.enums.status import status
import pytest
import logging
import os
import inspect

class gem_pytest(Executor):
    status = status # Adding status to reduce the number of imports by the user
    pytest = pytest
    def __init__(self):
        self.filepath=None
        testcase_name = inspect.currentframe().f_back.f_code.co_name  #Getting testcase name from the testcase file to display in report.
        super().__init__(tc_name=testcase_name)

    def assert_(self, expr):
        if not expr:
            # raise AssertionError
            self.reporter.addRow("Custom Assert Function","Expression evaluated as {}".format(expr),status.FAIL)
            logging.error("Assertion Error")
        else:
            self.reporter.addRow("Custom Assert Function","Expression evaluated as {}".format(expr),status.PASS)


    def run_tests(self):
        cmd = "pytest {} -p no:terminal".format(self.filepath) # Removing pytest logs to avoid confusion to the user
        returned_value = os.system(cmd)
        logging.info("Command Executed successfully......{}".format(returned_value))


