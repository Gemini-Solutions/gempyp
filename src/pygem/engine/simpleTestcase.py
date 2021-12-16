from abc import ABC, abstractmethod
from typing import List, Union, Dict
from pygem.config import DefaultSettings
from pygem.engine.baseTemplate import testcaseReporter


class AbstarctSimpleTestcase(ABC):
     
    @abstractmethod
    def main(self, testcaseSettings: Dict) -> Union(testcaseReporter, List[testcaseReporter]):
        """
            extend the baseTemplate and implement this method.
            :param testcaseSettings: testcasesettings object created from the testcase config
            :return
        """

    
    def RUN(self, testcaseSettings: Dict):
        """
            the main function which will be called by the executor
        """
        # set the values from the report if not set automatically 
        Data = []
        reports = self.main(testcaseSettings)

        if isinstance(reports, testcaseReporter):
            reports = [reports]
        
        for index, report in enumerate(reports):
            if not report.projectName:
                self.projectName = testcaseSettings.get("PROJECTNAME", "PYGEM")

            if not report.testcaseName:
                self.testcaseName = testcaseSettings.get("TESTCASENAME", f"TESTCASE_{index}")
 
            # call the destructor if not already called.
            report.finalize_report()

            # if user has not provided its own resultfile 
            if not report.resultFileName:
                report.resultFileName = report.templateData.makeReport(testcaseSettings.get("PYGEMFOLDER", DefaultSettings.DEFAULT_PYGEM_FOLDER))
            result = report.serialize()
            Data.append(result)

        return Data

