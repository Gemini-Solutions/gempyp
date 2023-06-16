import os
import logging
from typing import Dict
from datetime import datetime, timezone
from itertools import chain
import json
from gempyp.libs.enums.status import status
from gempyp.libs.common import findDuration, dateTimeEncoder
import traceback
from gempyp.libs.gem_s3_common import upload_to_s3, create_s3_link
from gempyp.config import DefaultSettings

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

        self.REPORTDATA["meta_data"] = metadata

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
        self.REPORTDATA["meta_data"].append(column2)
        self.REPORTDATA["meta_data"].append(column3)
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
    
    def makeSuiteReport(self, json_data, testcase_data, ouput_folder,jewel_user):
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
        reportJson["teststep_details"] = testcase_data
        repJson = reportJson
        # self.testcaseData = json.dumps(self.testcaseData)
        reportJson = json.dumps(reportJson)
        suiteReport = suiteReport.replace("DATA_1", reportJson)
        
        # if not len(testcase_data) > 0:   ##TODO
        #     return repJson, None
        ouput_file_path=""
        # if not jewel_user:
        ResultFile = os.path.join(ouput_folder, "Result_{}.html".format(date))
        ouput_file_path = ResultFile
        with open(ResultFile, "w+") as f:
            f.write(suiteReport)
        # return repJson, ouput_file_path
        return repJson
    
    def makeTestcaseReport(self):
        index_path = os.path.dirname(__file__)
        index_path = os.path.join(os.path.split(index_path)[0], "testcase.html")
        with open(index_path, "r") as f:
            Result_data = f.read()
        json_data = self._toJSON()
        return json.loads(json_data)
    
    def createLogFile(self,folder_path,output_file,suite_log_file):
        with open(output_file, 'a') as outfile:
            with open(suite_log_file, 'r') as infile:
                        # Read the contents of the file
                    file_contents = infile.read()
                    outfile.write(file_contents)
                    outfile.write('\n')
            # Iterate over all files in the folder
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.txt'):
                    file_path = os.path.join(folder_path, file_name)
                    
                    # Open each file in the folder
                    with open(file_path, 'r') as infile:
                        # Read the contents of the file
                        file_contents = infile.read()
                        
                        # Append the contents to the output file
                        outfile.write(file_contents)
                        outfile.write('\n')  # Add a newline after each file (optional)
        return output_file


    def repSummary(self, repJson,jewel_link, unuploaded_path,folder_path,output_file,bridgeToken,username,suite_log):
        """
        logging some information
        """
        try:
            logging.info("---------- Finalised the report --------------")
            logging.info("============== Run Summary =============")
            count_info = {key.lower(): val for key, val in repJson['suits_details']['testcase_info'].items()}
            log_str = f"Total Testcases: {str(count_info.get('total', 0))} | Passed Testcases: {str(count_info.get('pass', 0))} | Failed Testcases: {str(count_info.get('fail', 0))} | "
            status_dict = {"info": "Info", "warn": "WARN", "exe": "Exe", "err":"ERR"}
            for key, val in count_info.items():
                if key in status_dict.keys():
                    log_str += f"{status_dict[key.lower()]} Testcases: {val} | "
            logging.info(log_str.strip(" | "))
            output_file=self.createLogFile(folder_path,output_file,suite_log)
            s3_log_file_url=None
            try:
                s3_log_file_url = create_s3_link(url=upload_to_s3(DefaultSettings.urls["data"]["bucket-file-upload-api"], bridge_token=bridgeToken, username=username, file=output_file,tag="public")[0]["Url"])
            except Exception as e:
                logging.warn(str(e))

            if unuploaded_path != None:
                logging.info(f"Unuploaded Data File Path:{unuploaded_path}")
            #  we will check if output report is None, then display report not created
            if len(jewel_link)>0:
#                 s3_report_file_url= create_s3_link(url=upload_to_s3(DefaultSettings.urls["data"]["bucket-file-upload-api"], bridge_token=bridgetoken, username=username, file=output_file_path.split('/')[-1],tag="public")[0]["Url"]) 
                logging.info('Report at Jewel: {link}'.format(link = jewel_link))
#                 logging.info('Report at S3: {link}'.format(link = s3_report_file_url))
                
            # if not jewel_user:
                # logging.info('-------- Report created Successfully at: {path}'.format(path=output_file_path))


        except Exception as e:
            logging.error(traceback.format_exc(e))
