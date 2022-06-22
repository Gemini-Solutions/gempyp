from gempyp.engine.gempypHelper import Gempyp
from gempyp.engine.gempypHelper import Gempyp


class Combined(Gempyp):
    def __init__(self):
        pass

    def testcase_1(self):
        self.report = Gempyp("Gempyp", "testcase_1").reporter
        # need to user Gempyp.reporter directly here
        # no need to give testcase name and project name
        self.report.addRow("test", "desc", Gempyp.PASS)
        return self.report

    def testcase_2(self):
        self.report = Gempyp("Gempyp", "testcase_2").reporter
        self.report.addRow("main test", "main desc", self.PASS)
        return self.report
    
    def testcase_except_(self):
        self.report = Gempyp("Gempyp", "testcase_except").reporter
        x=3/0
        self.report.addRow(
           "test step3", "divide by 0: " +x, self.FAIL, extra_arg3="3", extra_arg2="2"
        )
        self.report.addMisc("Reason_Of_Failure", "Missing")
        # self.reporter.finalize_report()
        # self.reporter.templateData.makeReport("test")
        # print(self.reporter.serialize())

    def main(self):
        self.report = Gempyp("Gempyp", "main_test").reporter
        self.report.addRow("main_test", "desc", self.PASS)


