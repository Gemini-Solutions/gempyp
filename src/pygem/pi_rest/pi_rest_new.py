import os
import uuid
import traceback
from pygem.engine.baseTemplate import testcaseReporter as Base
from typing import Dict, List, Tuple, Type
from pygem.libs.enums.status import status
from pygem.pi_rest import api_common as api
from pygem.config import DefaultSettings
import logging
from pygem.libs import common
from pygem.engine.runner import getError
import time


class PIREST(Base):
    def __init__(self, data) -> Tuple[List, Dict]:
        logging.root.setLevel(logging.DEBUG)
        self.data = data
        logging.info("---------------------Inside REST FRAMEWORK------------------------")

        # set vars
        self.set_vars()

        # setting reporter object
        self.reporter = Base(projectName=self.data["PROJECTNAME"], testcaseName=self.data["configData"]["NAME"])

        logging.info("--------------------Report object created ------------------------")
        self.reporter.addRow("Starting Test", f'Testcase Name: {self.data["configData"]["NAME"]}', status.INFO) 

    def rest_engine(self):
        try:
            output, error = self.run()
        except Exception as e:
            common.errorHandler(logging, e, "Error occured while running the testcas")
            return None, getError(e, self.data["configData"])
        return output, error
    
    def run(self):
        # parse conf
        # set vars
        self.validate_conf()
        self.get_vals()

        # execute and format result 
        self.exec_request()
        self.reporter.finalize_report()
        output = self.write_to_report()
        return output, None

    def validate_conf(self):
        mandate = ["API", "METHOD", "HEADERS", "BODY"]
        if len(set(mandate) - set([i.upper() for i in self.data["configData"].keys()])) > 0:

            raise Exception("mandatory keys missing")
            
    # read config and get data
    def get_vals(self):

        # capitalize the keys
        for k, v in self.data["configData"].items():
            self.data.update({k.upper(): v})
        self.env = self.data.get("ENV", "PROD").strip().upper()

        # get the api url
        if self.env not in self.data.keys():
            self.api = self.data["configData"]["API"].strip()
        else: 
            self.api = self.data.get(self.env, "PROD").strip() + self.data["configData"]["API"].strip()

        # get the method
        self.method = self.data["configData"].get ("METHOD", "GET")

        # get the headers
        self.headers = self.data["configData"].get("HEADERS", {})
        self.headers = dict()

        # get body
        self.body = self.data["configData"].get("BODY", {})

        # get file
        self.file = self.data["configData"].get("REQUEST FILE", None)

    
    def exec_request(self):
        req_obj = api.Request()

        # create request
        req_obj.api = self.api
        req_obj.method = self.method
        req_obj.body = self.body
        req_obj.headers = self.headers
        req_obj.file = self.file

        # execute request
        res_obj = api.API().execute(req_obj)

        # get response
        self.response_body = res_obj.response_body
        self.starus_code = res_obj.status_code
        self.response_time = res_obj.response_time
        self.response_headers = res_obj.response_headers
        self.reporter.addRow("test step2", "hello world", status.PASS)
        
    def write_to_report(self):
        result = {}
        if not self.reporter.resultFileName:
            try:
                try:
                    os.makedirs(self.data.get("OUTPUT_FOLDER", self.default_report_path))
                except Exception as e:
                    print(traceback.print_exc())
                self.reporter.jsonData = self.reporter.templateData.makeReport(
                    self.data.get("OUTPUT_FOLDER"), self.reporter.testcaseName + str(time.time()))
                self.jsonData = self.reporter.jsonData
                print(self.jsonData)
                result = self.reporter.serialize()
                # make report
                # self.makeReport(json.dumps(self.reporter.jsonData))
                # print("-------file_dumped---------")

            except Exception as e:
                print(traceback.print_exc())
        output = []
        tempdict = {} 
        tc_run_id = f"{self.data['NAME']}_{uuid.uuid4()}"
        tempdict["tc_run_id"] = tc_run_id
        tempdict["name"] = result["NAME"]
        tempdict["category"] = self.data.get("CATEGORY")
        tempdict["status"] = result["STATUS"]
        tempdict["user"] = self.data.get("USER")
        tempdict["machine"] = self.data.get("MACHINE")
        tempdict["product_type"] = "PYGEM"
        tempdict["result_file"] = result["RESULT_FILE"]
        tempdict["start_time"] = result["START_TIME"]
        tempdict["end_time"] = result["END_TIME"]
        tempdict["ignore"] = False
        all_status = result["jsonData"]["metaData"][2]
        total = 0
        for key in all_status:
            total = all_status[key]
        result["jsonData"]["metaData"][2]["TOTAL"] = total

        # have to look into the way on how to get the log file
        tempdict["log_file"] = None

        singleTestcase = {}
        singleTestcase["testcaseDict"] = tempdict
        singleTestcase["misc"] = result.get("MISC")
        singleTestcase["jsonData"] = self.jsonData
        output.append(singleTestcase)
        return output

    def makeReport(self, jsonData):
        index_path = os.path.dirname(__file__)
        Result_data = ""
        index_path = os.path.join(os.path.split(index_path)[0], "testcase.html")
        with open(index_path, "r") as f:
            Result_data = f.read()

        Result_data = Result_data.replace("::DATA::", jsonData)

        result_file = os.path.join(self.data.get("OUTPUT_FOLDER"), f"{self.reporter.testcaseName + str(time.time())}.html")
        with open(result_file, "w+") as f:
            f.write(Result_data)

    def set_vars(self):
        self.default_report_path = os.path.join(os.getcwd(), "pi_rest_reports")
        self.data["OUTPUT_FOLDER"] = self.data.get("OUTPUT_FOLDER", self.default_report_path)
        if self.data["OUTPUT_FOLDER"].strip() == "":
            self.data["OUTPUT_FOLDER"] = self.default_report_path
