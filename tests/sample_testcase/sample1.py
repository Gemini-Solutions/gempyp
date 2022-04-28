from pygem.engine.simpleTestcase import AbstarctSimpleTestcase
from pygem.engine.baseTemplate import testcaseReporter
from pygem.libs.enums.status import status


class sample1(AbstarctSimpleTestcase):
    def main(self, testcaseSettings, **kwargs):

        self.verify(kwargs["PROJECTNAME"], testcaseSettings["NAME"])
        return self.reporter

    def verify(self, projectName, testcaseName):
        self.reporter = testcaseReporter(projectName, testcaseName)

        self.reporter.addRow(
            "test step1", "hello world", status.PASS, extra_arg="1", extra_arg2="2"
        )
        self.reporter.addRow(
            "test step2", "hello world", status.FAIL, extra_arg3="3", extra_arg2="2"
        )
        self.reporter.addMisc("Reason_Of_Failure","Missing")
        # self.reporter.finalize_report()
        # self.reporter.templateData.makeReport("test")
        # print(self.reporter.serialize())


if __name__ == "__main__":
    sample1().verify("testProject", "sampleTestcase1")
