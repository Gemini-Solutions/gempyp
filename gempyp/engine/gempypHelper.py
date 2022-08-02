from gempyp.engine.simpleTestcase import AbstractSimpleTestcase
from gempyp.engine.baseTemplate import testcaseReporter


class Gempyp(AbstractSimpleTestcase):
    def __init__(self, projectName=None, testcaseName=None):
        if projectName is not None and testcaseName is not None:
            self.reporter = testcaseReporter(projectName, testcaseName)
        else:
            self.reporter = testcaseReporter("Gempyp", "testing")
        
        # access project name and testcase name
        # self.reporter = testcaseReporter(Project, Testcase)
        # user will use this reporter in their testcases
        


        