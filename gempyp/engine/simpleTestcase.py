from abc import ABC
from typing import List, Union, Dict
from gempyp.config import DefaultSettings
from gempyp.engine.baseTemplate import TestcaseReporter
from gempyp.libs import common
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
                # code for finding exception and writing reason of failure 
                # exceptiondata = traceback.format_exc().splitlines()
                # exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
                # reporter.addMisc("Reason of Failure",exceptionarray[0])

                # reports = TestcaseReporter(kwargs["PROJECT_NAME"], testcase_settings["NAME"])
                reporter.addMisc("REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), err))
                reporter.addRow("Exception Occured", str(error) + 'at' + str(info), status.ERR)
            finally:
                return reporter
                
        except Exception as e:
            if e:            
                logger.error(traceback.format_exc())
                # exceptiondata = traceback.format_exc().splitlines()
                # exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
                # reporter.addMisc("Reason of Failure",exceptionarray[0])
                reporter.addMisc("REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))
            
        

    def RUN(self, cls, testcase_settings: Dict, **kwargs) -> List:
        """
        the main function which will be called by the executor
        take argument as testcaseDict and call the gempypMethodExecutor() method
        and later on call basetemplate finalizereport method and reurn data to testcaseRunner method 
        """
        # set the values from the report if not s et automatically
        self.logger = testcase_settings.get('LOGGER')
        Data = []

        try:
            self.logger.info('================= Running Testcase: {testcase} ============'.format(testcase=testcase_settings["NAME"]))
            reports = self.gempypMethodExecutor(cls, testcase_settings, **kwargs)

        except Exception:
            etype, value, tb = sys.exc_info()
            self.logger.error(traceback.format_exc())
            info, error = traceback.format_exception(etype, value, tb)[-2:]
            reports = TestcaseReporter(kwargs["PROJECT_NAME"], testcase_settings["NAME"])
            reports.addRow("Exception Occured", str(error) + 'at' + str(info), status.ERR)


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