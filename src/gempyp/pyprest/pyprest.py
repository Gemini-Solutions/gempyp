import os
import traceback
import time
import logging
import importlib
from typing import Dict, List, Tuple
from gempyp.engine.baseTemplate import testcaseReporter as Base
from gempyp.libs.enums.status import status
from gempyp.pyprest import api_common as api
from gempyp.libs import common
from gempyp.engine.runner import getError
from gempyp.pyprest.Reporting import write_to_report
from gempyp.pyprest.pre_variables import pre_variables
from gempyp.pyprest.variable_replacement import variable_replacement as var_replacement
from gempyp.pyprest.post_variables import post_variables
from gempyp.pyprest.key_check import key_check
from gempyp.pyprest.post_assertion import post_assertion
from gempyp.pyprest.rest_obj import REST_Obj


class PYPREST(Base):
    def __init__(self, data) -> Tuple[List, Dict]:
        logging.root.setLevel(logging.DEBUG)
        self.data = data
        logging.info("---------------------Inside REST FRAMEWORK------------------------")

        # set vars
        self.set_vars()

        # setting reporter object
        self.reporter = Base(projectName=self.project, testcaseName=self.tcname)

        logging.info("--------------------Report object created ------------------------")
        self.reporter.addRow("Starting Test", f'Testcase Name: {self.tcname}', status.INFO) 


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
        self.env = self.data.get("ENV", "PROD").strip(" ").upper()

        # get the api url
        if self.env not in self.data.keys():
            self.api = self.data["configData"]["API"].strip(" ")
        else: 
            self.api = self.data.get(self.env, "PROD").strip(" ") + self.data["configData"]["API"].strip(" ")

        # get the method
        self.method = self.data["configData"].get ("METHOD", "GET")

        # get the headers
        self.headers = self.data["configData"].get("HEADERS", {})
        self.headers = dict()

        # get body
        self.body = self.data["configData"].get("BODY", {})

        # get file
        self.file = self.data["configData"].get("REQUEST_FILE", None)

        self.pre_variables = self.data["configData"].get("PRE_VARIABLES", "")

        self.key_check = self.data["configData"].get("KEY_CHECK", None)

        self.post_assertion = self.data["configData"].get("POST_ASSERTION", None)

        self.post_variables = self.data["configData"].get("POST_VARIABLE", "")

        #setting variables and variable replacement
        pre_variables(self).pre_variable()
        var_replacement(self).variable_replacement()
    
    def exec_request(self):
        self.req_obj = api.Request()
        # create request
        self.req_obj.api = self.api
        self.req_obj.method = self.method
        self.req_obj.body = self.body
        self.req_obj.headers = self.headers
        self.req_obj.file = self.file

        self.log_request()

        # calling the before method after creating the request object.
        self.before_method()

        # calling variable replacement after before method
        var_replacement(self).variable_replacement()

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
        self.default_report_path = os.path.join(os.getcwd(), "pyprest_reports")
        self.data["OUTPUT_FOLDER"] = self.data.get("OUTPUT_FOLDER", self.default_report_path)
        if self.data["OUTPUT_FOLDER"].strip(" ") == "":
            self.data["OUTPUT_FOLDER"] = self.default_report_path
        self.project = self.data["PROJECTNAME"]
        self.tcname = self.data["configData"]["NAME"]
        self.legacy_req = None
        self.req_obj = None
        self.res_obj = None
        self.legacy_res = None
        self.request_file = None
        self.env = self.data["ENV"]
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
        logging.info("CHECKING FOR BEFORE FILE___________________________")
        file_str = self.data["configData"].get("BEFORE_FILE", "")
        if file_str == "" or file_str == " ":
            logging.info("BEFORE FILE NOT FOUND___________________________")
            return
        file_name = file_str.split("path=")[1].split(",")[0]
        if "CLASS=" in file_str.upper():
            class_name = file_str.split("class=")[1].split(",")[0]
        else:
            class_name = ""
        if "METHOD=" in file_str.upper():
            method_name = file_str.split("method=")[1].split(",")[0]
        else:
            method_name = "before"
        
        logging.info("Before file path:- " + file_name)
        logging.info("Before file class:- " + class_name)
        logging.info("Before file mthod:- " + method_name)
        try:
            file_obj = importlib.import_module(file_name)
            print("file_obj - ", file_obj)
            obj_ = file_obj
            before_obj = REST_Obj(
                pg=self.reporter,
                project=self.project,
                request=self.req_obj,
                response=self.res_obj,
                tcname=self.tcname,
                variables=self.variables,
                legacy_req=self.legacy_req,
                legacy_res=self.legacy_res,
                request_file=self.file,
                env=self.env,
            )
            if class_name != "":
                obj_ = getattr(file_obj, class_name)()
            fin_obj = getattr(obj_, method_name)(before_obj)
            self.extract_obj(fin_obj)
            
        except Exception:
            traceback.print_exc()
        var_replacement(self).variable_replacement()
        pass

    def after_method(self):
        # check for after file
        logging.info("CHECKING FOR AFTER FILE___________________________")
        file_str = self.data["configData"].get("AFTER_FILE", "")
        if file_str == "" or file_str == " ":
            logging.info("AFTER FILE NOT FOUND___________________________")
            return
        file_name = file_str.split("path=")[1].split(",")[0]
        if "CLASS=" in file_str.upper():
            class_name = file_str.split("class=")[1].split(",")[0]
        else:
            class_name = ""
        if "METHOD=" in file_str.upper():
            method_name = file_str.split("method=")[1].split(",")[0]
        else:
            method_name = "after"
        logging.info("After file path:- " + file_name)
        logging.info("After file class:- " + class_name)
        logging.info("After file mthod:- " + method_name)
        try:
            file_obj = importlib.import_module(file_name)
            print("file_obj - ", file_obj)
            obj_ = file_obj
            after_obj = REST_Obj(
                pg=self.reporter,
                project=self.project,
                request=self.req_obj,
                response=self.res_obj,
                tcname=self.tcname,
                variables=self.variables,
                legacy_req=self.legacy_req,
                legacy_res=self.legacy_res,
                request_file=self.file,
                env=self.env,
            )
            if class_name != "":
                obj_ = getattr(file_obj, class_name)()
            fin_obj = getattr(obj_, method_name)(after_obj)
            self.extract_obj(fin_obj)
        except Exception:
            pass
        var_replacement(self).variable_replacement()
        pass

    def extract_obj(self, obj):
        self.reporter = obj.pg
        self.project = obj.project
        self.req_obj = obj.request
        self.res_obj = obj.response
        self.tcname = obj.tcname
        self.variables = obj.variables
        self.legacy_req = obj.legacy_req
        self.legacy_res = obj.legacy_res
        self.file = obj.request_file
        self.env = obj.env
