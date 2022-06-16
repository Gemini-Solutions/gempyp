from abc import ABC, abstractmethod
from typing import List, Union, Dict
from gempyp.config import DefaultSettings
from gempyp.engine.baseTemplate import testcaseReporter
from gempyp.libs.enums.status import status
import logging
from gempyp.libs.common import moduleImports


class AbstarctSimpleTestcase(ABC):
    def gempypMethodExecutor(
        self, cls, testcaseSettings: Dict, **kwargs
    ) -> testcaseReporter:
        """
        extend the baseTemplate and implement this method.
        :param testcaseSettings: testcasesettings object created from the testcase config
        :return
        """
        file_name = testcaseSettings.get("PATH")
        try:
            testcase = moduleImports(file_name)
        except:
            logging.ERROR("Testcase not imported")
        try:
            methodName = testcaseSettings.get("METHOD", "main")
            print("-------- method ---------", methodName)
            try:
                methodName = getattr(cls(), methodName)
                report = methodName()
                return report
            except Exception as err:
                logging.info("Could not run the method")
                
        except Exception as e:                
            print(e)
            
        

    def RUN(self, cls, testcaseSettings: Dict, **kwargs) -> List:
        """
        the main function which will be called by the executor
        """
        # set the values from the report if not s et automatically
        Data = []
        reports = self.gempypMethodExecutor(cls, testcaseSettings, **kwargs)

        if isinstance(reports, testcaseReporter):
            reports = [reports]

        for index, report in enumerate(reports):
            if not report.projectName:
                report.projectName = testcaseSettings.get("PROJECTNAME", "GEMPYP")

            if not report.testcaseName:
                report.testcaseName = testcaseSettings.get("NAME", "TESTCASE")
                report.testcaseName = f"{self.testcaseName}_{index}"

            # call the destructor if not already called.
            report.finalize_report()

            # if user has not provided its own resultfile
            if not report.resultFileName:
                report.jsonData = report.templateData.makeReport(
                    kwargs.get(
                        "OUTPUT_FOLDER", DefaultSettings.DEFAULT_GEMPYP_FOLDER
                    ), testcaseSettings["NAME"])
            result = report.serialize()
            Data.append(result)

        return Data
