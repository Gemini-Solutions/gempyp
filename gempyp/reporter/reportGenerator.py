import os
import logging
from typing import Dict
from datetime import datetime, timezone
from itertools import chain
import json
from gempyp.libs.enums.status import status
from gempyp.libs.common import findDuration, dateTimeEncoder
import traceback


class TemplateData:
    def __init__(self, header="Gemini Report"):
        # initliza the data to be stored as a JSON
        self.REPORTDATA = {"Header": header, "steps": []}

    def newReport(self, project_name: str, tescase_name: str):
        metadata = []
        self.kwargs_list=[]
        # 1st Column
        column1 = {
            "TESTCASE NAME": tescase_name,
            "SERVICE PROJECT": project_name,
            "DATE OF EXECUTION": {"value": datetime.now(timezone.utc), "type": "date"},
        }
        metadata.append(column1)

        self.REPORTDATA["metaData"] = metadata

    def newRow(self, title: str, description: str, status: status, **kwargs):
        step = {"Step Name": title, "Step Description": description, "status": status}
        if not kwargs.get("attachment"):
            kwargs.pop("attachment")
        if kwargs:
            if kwargs not in self.kwargs_list:
                self.kwargs_list.append(kwargs)
        step.update(kwargs)
        self.REPORTDATA["steps"].append(step)

    # finalize the result. Calculates duration etc.
    def finalizeResult(
        self, begin_time: datetime, end_time: datetime, status_counts: Dict
    ):
        # column2
        column2 = {
            "EXECUTION STARTED ON": {"value": begin_time, "type": "datetime"},
            "EXECUTION ENDED ON": {"value": end_time, "type": "datetime"},
            "EXECUTION DURATION": findDuration(begin_time, end_time),
        }

        # column3
        column3 = {k.name: v for k, v in status_counts.items()}
        self.REPORTDATA["metaData"].append(column2)
        self.REPORTDATA["metaData"].append(column3)
        # filters
        # self.REPORTDATA["FilterNames"] = self._getFilters()
        # filter_values = {}
        # filter_values["status"] = [value.name for value in status_counts.keys()]
        # self.REPORTDATA["FilterValues"] = filter_values

    """def _getFilters(self) -> Dict:
        
        # return the unique columns

        filter_names = list(
            set(chain.from_iterable(step.keys() for step in self.REPORTDATA["steps"]))
        )
        # filter_names.pop("status")
        filter_dict = {name: "Input" for name in filter_names}
        filter_dict["status"] = "Dropdown"

        return filter_dict"""

    # Converts the data to the JSON
    def _toJSON(self) -> str:
        """
        dump the data in REPORTDATA
        """
        kwargs_list_comm =  dict(j for i in self.kwargs_list for j in i.items())
        lis = kwargs_list_comm.keys()
        for i in self.REPORTDATA["steps"]:
            for j in lis:
                if j in i:
                    continue
                else:
                    i.update({j:"-"})

        try:
            result_data = json.dumps(self.REPORTDATA, cls=dateTimeEncoder)
            return result_data
        except TypeError as error:
            logging.error("Error occured while serializing the testcase Result Data")
            logging.error(f"Error: {error}")
        except Exception as e:
            logging.error("some Error occured")
            logging.error(f"Error: {e}")
        return "Error"
    
    def makeSuiteReport(self, json_data, testcase_data, ouput_folder):
        """
        saves the report json 
        """
        suiteReport = None
        date = datetime.now().strftime("%Y_%b_%d_%H%M%S_%f")

        suite_path = os.path.dirname(__file__)
        suite_path = os.path.join(os.path.split(suite_path)[0], "final_report.html")
        with open(suite_path, "r") as f:
            suiteReport = f.read()

        reportJson = json_data
        reportJson = json.loads(reportJson)
        reportJson["TestStep_Details"] = testcase_data
        repJson = reportJson
        # self.testcaseData = json.dumps(self.testcaseData)
        reportJson = json.dumps(reportJson)
        suiteReport = suiteReport.replace("DATA_1", reportJson)

        ResultFile = os.path.join(ouput_folder, "Result_{}.html".format(date))
        ouput_file_path = ResultFile
        with open(ResultFile, "w+") as f:
            f.write(suiteReport)
        return repJson, ouput_file_path
    
    def makeTestcaseReport(self):
        index_path = os.path.dirname(__file__)
        index_path = os.path.join(os.path.split(index_path)[0], "testcase.html")
        with open(index_path, "r") as f:
            Result_data = f.read()
        json_data = self._toJSON()
        return json.loads(json_data)

    def repSummary(self, repJson, output_file_path, jewel_link, failed_testcases, unuploaded_path):
        """
        logging some information
        """
        try:
            logging.info("---------- Finalised the report --------------")
            logging.info("============== Run Summary =============")
            count_info = {key.lower(): val for key, val in repJson['Suits_Details']['testcase_info'].items()}
            log_str = f"Total Testcases: {str(count_info.get('total', 0))} | Passed Testcases: {str(count_info.get('pass', 0))} | Failed Testcases: {str(count_info.get('fail', 0))} | "
            status_dict = {"info": "Info", "warn": "WARN", "exe": "Exe", "err":"ERR"}
            for key, val in count_info.items():
                if key in status_dict.keys():
                    log_str += f"{status_dict[key.lower()]} Testcases: {val} | "
            logging.info(log_str.strip(" | "))

            if failed_testcases != 0:
                logging.info(f"Number of Testcases not Uploaded:{failed_testcases}")
                logging.info(f"Unuploaded Testcase File Path:{unuploaded_path}")
            
            if len(jewel_link)>0:
                logging.info('Report at Jewel: {link}'.format(link = jewel_link))
            logging.info('-------- Report created Successfully at: {path}'.format(path=output_file_path))


        except Exception as e:
            logging.error(traceback.print_exc(e))
