from gempyp.engine.simpleTestcase import AbstractSimpleTestcase


class Combined(AbstractSimpleTestcase):
    def __init__(self):
        pass

    def testcase_1(self, reporter):
        reporter.addRow("test", "desc", self.Status.PASS)
        reporter.logger.info("Testing logger -  this is testcase 1--------------------------")
        reporter.addMisc("TEST 1", "Test")

        return reporter

    def testcase_2(self, reporter):
        reporter.logger.info("Here we are testing logger")
        reporter.logger.info("this is testcase 2--------------------------")
        reporter.addRow("main test", "main desc", self.Status.PASS)
        reporter.addMisc("TEST 2", "Test___")

        return reporter
    
    def testcase_except_(self, reporter):
        reporter.logger.info("this is the exception testcase")
        reporter.addRow("except test", "main desc", self.Status.PASS)

        x=3/0
        reporter.logger.info("this is the exception testcase")
        reporter.addRow("except test", "main desc", self.Status.PASS)

        reporter.addRow(
           "test step3", "divide by 0: " +x, self.Status.FAIL, extra_arg3="3", extra_arg2="2"
        )
        reporter.addMisc("Reason_Of_Failure", "Missing")

    def main(self, reporter):
        reporter.addRow("main_test", "desc", self.Status.PASS)
        return reporter


