from gempyp.engine.simpleTestcase import AbstarctSimpleTestcase
from gempyp.engine.baseTemplate import testcaseReporter


class Gempyp(AbstarctSimpleTestcase):
    def __init__(self, projectName=None, testcaseName=None):
        if projectName is not None and testcaseName is not None:
            self.reporter = testcaseReporter(projectName, testcaseName)
        else:
            self.reporter = testcaseReporter("Gempyp", "testing")


        