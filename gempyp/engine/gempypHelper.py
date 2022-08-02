from gempyp.engine.simpleTestcase import AbstarctSimpleTestcase
from gempyp.engine.baseTemplate import TestcaseReporter


class Gempyp(AbstarctSimpleTestcase):
    def __init__(self, project_name=None, testcase_name=None):
        if project_name is not None and testcase_name is not None:
            self.reporter = TestcaseReporter(project_name, testcase_name)
        else:
            self.reporter = TestcaseReporter("Gempyp", "testing")
        
        # access project name and testcase name
        # self.reporter = TestcaseReporter(Project, Testcase)
        # user will use this reporter in their testcases
        


        