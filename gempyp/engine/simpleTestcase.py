from abc import ABC, abstractmethod
from typing import List, Union, Dict
from gempyp.config import DefaultSettings
from gempyp.engine.baseTemplate import TestcaseReporter
from gempyp.libs.common import moduleImports
import sys,traceback
from gempyp.libs.enums.status import status
import logging


class AbstractSimpleTestcase(ABC):
    Status = status
    # get logger

    def gempypMethodExecutor(
        self, cls, testcase_settings: Dict, **kwargs
    ) -> TestcaseReporter:
        """
        extend the baseTemplate and implement this method.
        :param testcase_settings: testcasesettings object created from the testcase config
        :return
        """
        logger = testcase_settings.get("LOGGER")
        kwargs["TESTCASENAME"] = testcase_settings["NAME"]
        file_name = testcase_settings.get("PATH")
        try:
            testcase = moduleImports(file_name)
        except:
            logger.ERROR("Testcase not imported")
        try:
            method_name = testcase_settings.get("METHOD", "main")
            logger.info(f"-------- method ---------{method_name}")
            reporter = TestcaseReporter(kwargs["PROJECT_NAME"], testcase_settings["NAME"])
            # adding logger to the reporter
            reporter.logger = logger
            try:
                method_name = getattr(cls(), method_name)
                method_name(reporter)
            except Exception as err:
                logger.error(traceback.format_exc())
                etype, value, tb = sys.exc_info()
                info, error = traceback.format_exception(etype, value, tb)[-2:]
                #reports = TestcaseReporter(kwargs["PROJECT_NAME"], testcase_settings["NAME"])
                reporter.addRow("Exception Occured", str(error) + 'at' + str(info), status.FAIL)
            finally:
                return reporter
                
        except Exception as e:
            if e:            
                logger.error(traceback.format_exc())
            
        

    def RUN(self, cls, testcase_settings: Dict, **kwargs) -> List:
        """
        the main function which will be called by the executor
        """
        # set the values from the report if not s et automatically
        self.logger = testcase_settings.get('LOGGER')
        Data = []

        try:
            self.logger.info('================= Running Testcase: {testcase} ============'.format(testcase=testcase_settings["NAME"]))
            reports = self.gempypMethodExecutor(cls, testcase_settings, **kwargs)

            # will never enter this  block
            # if reports is None:
            #     reports = TestcaseReporter(kwargs["PROJECT_NAME"], testcase_settings["NAME"])
            #     self.logger.error("Report object was not returned from the testcase file")
            #     reports.addRow("Exception Occured", "Exception occured in testcase: Report was not generated.", status.FAIL)    
        except Exception:
            etype, value, tb = sys.exc_info()
            self.logger.error(traceback.format_exc())
            info, error = traceback.format_exception(etype, value, tb)[-2:]
            reports = TestcaseReporter(kwargs["PROJECT_NAME"], testcase_settings["NAME"])
            reports.addRow("Exception Occured", str(error) + 'at' + str(info), status.FAIL)

        if isinstance(reports, TestcaseReporter):
            reports = [reports]

        for index, report in enumerate(reports):
            if not report.project_name:
                report.project_name = testcase_settings.get("PROJECTNAME", "GEMPYP")

            if not report.testcase_name:
                report.testcase_name = testcase_settings.get("NAME", "TESTCASE")
                report.testcase_name = f"{self.testcase_name}_{index}"

            # call the destructor if not already called.
            report.finalizeReport()
            # if user has not provided its own resultfile
            if not report.result_file_name:
                report.json_data = report.template_data.makeTestcaseReport()
            result = report.serialize()
            Data.append(result)

        return Data
