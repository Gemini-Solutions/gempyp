import os
import logging
from typing import Dict
from datetime import datetime, timezone
from itertools import chain
import json
from gempyp.libs.enums.status import status
from gempyp.libs.common import findDuration, dateTimeEncoder
import traceback


class templateData:
    def __init__(self, header="Gemini Report"):
        # initliza the data to be stored as a JSON
        self.REPORTDATA = {"Header": header, "steps": []}

    def newReport(self, projectName: str, tescaseName: str):
        metadata = []
        # 1st Column
        column1 = {
            "TESTCASE NAME": tescaseName,
            "SERVICE PROJECT": projectName,
            "DATE OF EXECUTION": {"value": datetime.now(timezone.utc), "type": "date"},
        }
        metadata.append(column1)

        self.REPORTDATA["metaData"] = metadata

    def newRow(self, title: str, description: str, status: status, **kwargs):
        step = {"title": title, "description": description, "status": status}

        if not kwargs.get("attachment"):
            kwargs.pop("attachment")

        step.update(kwargs)

        self.REPORTDATA["steps"].append(step)

    # finalize the result. Calulates duration etc.
    def finalizeResult(
        self, beginTime: datetime, endTime: datetime, statusCounts: Dict
    ):
        # column2
        column2 = {
            "EXECUTION STARTED ON": {"value": beginTime, "type": "datetime"},
            "EXECUTION ENDED ON": {"value": endTime, "type": "datetime"},
            "EXECUTION DURATION": findDuration(beginTime, endTime),
        }

        # column3
        column3 = {k.name: v for k, v in statusCounts.items()}
        self.REPORTDATA["metaData"].append(column2)
        self.REPORTDATA["metaData"].append(column3)
        self.REPORTDATA["FilterNames"] = self._getFilters()
        filterValues = {}
        filterValues["status"] = [value.name for value in statusCounts.keys()]
        self.REPORTDATA["FilterValues"] = filterValues

    def _getFilters(self) -> Dict:
        """
        return the unique columns
        """

        filterNames = list(
            set(chain.from_iterable(step.keys() for step in self.REPORTDATA["steps"]))
        )
        # filterNames.pop("status")
        filterDict = {name: "Input" for name in filterNames}
        filterDict["status"] = "Dropdown"

        return filterDict

    # Converts the data to the JSON
    def _toJSON(self) -> str:
        """
        dump the data in REPORTDATA
        """
        try:
            ResultData = json.dumps(self.REPORTDATA, cls=dateTimeEncoder)

            return ResultData
        except TypeError as error:
            logging.error("Error occured while serializing the testcase Result Data")
            logging.error(f"Error: {error}")
        except Exception as e:
            logging.error("some Error occured")
            logging.error(f"Error: {e}")
        return "Error"
    
    def makeSuiteReport(self, jsonData, testcaseData, ouput_folder):
        """
        saves the report json 
        """
        print(jsonData, "=========================")
        print(testcaseData, "888888888888888888888888888888")
        suiteReport = None
        date = datetime.now().strftime("%Y_%b_%d_%H%M%S_%f")

        suite_path = os.path.dirname(__file__)
        suite_path = os.path.join(os.path.split(suite_path)[0], "final_report.html")
        with open(suite_path, "r") as f:
            suiteReport = f.read()

        reportJson = jsonData
        reportJson = json.loads(reportJson)
        reportJson["TestStep_Details"] = testcaseData
        repJson = reportJson
        # self.testcaseData = json.dumps(self.testcaseData)
        reportJson = json.dumps(reportJson)
        suiteReport = suiteReport.replace("DATA_1", reportJson)

        ResultFile = os.path.join(ouput_folder, "Result_{}.html".format(date))
        ouput_file_path = ResultFile
        with open(ResultFile, "w+") as f:
            f.write(suiteReport)
        return repJson, ouput_file_path
    
    def makeTestcaseReport(self, Result_Folder, name):
        index_path = os.path.dirname(__file__)
        index_path = os.path.join(os.path.split(index_path)[0], "testcase.html")
        with open(index_path, "r") as f:
            Result_data = f.read()
        jsonData = self._toJSON()
        return json.loads(jsonData)

    def repSummary(self, repJson, output_file_path):
        """
        logging some information
        """
        try:
            logging.info("---------- Finalised the report --------------")
            logging.info("============== Run Summary =============")
            count_info = {key.lower(): val for key, val in repJson['Suite_Details']['Testcase_Info'].items()}
            log_str = f"Total Testcases: {str(count_info.get('total', 0))} | Passed Testcases: {str(count_info.get('pass', 0))} | Failed Testcases: {str(count_info.get('fail', 0))} | "
            status_dict = {"info": "Info", "warn": "WARN", "exe": "Exe"}
            for key, val in count_info.items():
                if key in status_dict.keys():
                    log_str += f"{status_dict[key.lower()]} Testcases: {val} | "
        

            logging.info(log_str.strip(" | "))
            
            logging.info('-------- Report created Successfully at: {path}'.format(path=output_file_path))


        except Exception as e:
            logging.error(traceback.print_exc(e))