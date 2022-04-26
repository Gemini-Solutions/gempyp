import os
import traceback
import time
import logging
from typing import Dict, List, Tuple
from pygem.engine.baseTemplate import testcaseReporter as Base
from pygem.libs.enums.status import status
from pygem.pi_rest import api_common as api
from pygem.libs import common
from pygem.engine.runner import getError
from pygem.pi_rest.Reporting import write_to_report
from pygem.pi_rest.pre_variables import pre_variables
from pygem.pi_rest.variable_replacement import variable_replacement as var_replacement
from pygem.pi_rest.post_variables import post_variables
from pygem.pi_rest.key_check import key_check
from pygem.pi_rest.post_assertion import post_assertion


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
        output = []
        try:
            self.validate_conf()
            output, error = self.run()
            return output, error
        except Exception as e:
            common.errorHandler(logging, e, "Error occured while running the testcas")

            return None, getError(e, self.data["configData"])
    
    def run(self):
        # parse conf
        # set vars
        # self.validate_conf()
        self.get_vals()

        # execute and format result 
        self.exec_request()
        self.post_process()
        self.reporter.finalize_report()
        output = write_to_report(self)
        return output, None

    def validate_conf(self):
        mandate = ["API", "METHOD", "HEADERS", "BODY"]
        # ---------------------------------------adding misc data -----------------------------------------------------
        # self.reporter.addMisc(Misc="Test data")
        # self.reporter._miscData["Reason_of_failure"] = "Mandatory keys are missing"

        # ------------------------------adding columns to testcase file-----------------------------------------------
        # self.reporter.addRow("User Profile Data cannot be fetched", "Token expired or incorrect", status.FAIL, test="test")

        if len(set(mandate) - set([i.upper() for i in self.data["configData"].keys()])) > 0:
            # update reason of failure in misc
            self.reporter._miscData["Reason_of_failure"] = "Mandatory keys are missing"
            # return None, getError("missing keys", self.data["configData"])
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
        self.file = self.data["configData"].get("REQUEST_FILE", None)

        self.pre_variables = self.data["configData"].get("PRE_VARIABLES", {})

        self.key_check = self.data["configData"].get("KEY_CHECK", None)

        self.post_assertion = self.data["configData"].get("POST_ASSERTION", None)

        self.post_variable = self.data["configData"].get("POST_VARIABLE", {})

        #setting variables and variable replacement
        pre_variables(self).pre_variable()
        var_replacement(self).variable_replacement()
        self.before_method()

    
    def exec_request(self):
        self.req_obj = api.Request()
        # create request
        self.req_obj.api = self.api
        self.req_obj.method = self.method
        self.req_obj.body = self.body
        self.req_obj.headers = self.headers
        self.req_obj.file = self.file

        self.log_request()
        try:
            # execute request
            self.res_obj = api.API().execute(self.req_obj)
            # self.res_obj.response_body
            # self.res_obj.status_code
            # self.res_obj.response_time
            # self.res_obj.response_headers
            self.log_response()
        except Exception as e:
            traceback.print_exc()
            self.reporter.addRow("Executing API", "Some error occurred while hitting the API", status.FAIL)

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

        self.variables = {}

    def log_request(self):
        body_str = "</br><b>REQUEST BODY</b>: {self.req_obj.body}" if self.req_obj.method.upper() != "GET" else ""
        self.reporter.addRow("Executing the REST Endpoint", 
                             f"<b>URL</b>: {self.req_obj.api}</br>" 
                             + f"<b>METHOD</b>: {self.req_obj.method}</br>" 
                             + f"<b>REQUEST HEADERS</b>: {self.req_obj.headers}" 
                             + body_str, 
                             status.PASS)

    def log_response(self):
        self.reporter.addRow("Details of Request Execution", 
                             f"<b>RESPONSE CODE</b>: {self.res_obj.status_code}</br>" 
                             + f"<b>RESPONSE HEADERS</b>: {self.res_obj.response_headers}</br>" 
                             + f"<b>RESPONSE BODY</b>: {self.res_obj.response_body}", 
                             status.INFO)
        """self.reporter.addRow("Details of Request Execution", 
                             f"<b>RESPONSE CODE</b>: {self.res_obj.status_code}</br>" 
                             + f"<b>RESPONSE HEADERS</b>: {self.res_obj.response_headers}</br>" , 
                             status.INFO)"""

    def post_process(self):
        post_variables(self).post_variables()
        key_check(self).key_check()
        post_assertion(self).post_assertion()
        self.after_method()

    def before_method(self):
        # check for before_file
        var_replacement(self).variable_replacement()
        pass

    def after_method(self):
        # check for after file
        var_replacement(self).variable_replacement()
        pass
