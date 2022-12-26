from asyncio.log import logger
import os
import traceback
import logging
import json
from typing import Dict, List, Tuple
from gempyp.engine.baseTemplate import TestcaseReporter as Base
from gempyp.libs.enums.status import status
from gempyp.pyprest import apiCommon as api
from gempyp.libs import common
from gempyp.engine.runner import getError
from gempyp.pyprest.reporting import writeToReport
from gempyp.pyprest.preVariables import PreVariables
from gempyp.pyprest.variableReplacement import VariableReplacement as VarReplacement
from gempyp.pyprest.postVariables import PostVariables
from gempyp.pyprest.keyCheck import KeyCheck
from gempyp.pyprest.postAssertion import PostAssertion
from gempyp.pyprest.restObj import RestObj
from gempyp.pyprest.miscVariables import MiscVariables
from gempyp.libs.common import moduleImports
from gempyp.libs.gem_s3_common import download_from_s3
# from gempyp.libs import custom_s3


class PypRest(Base):
    def __init__(self, data) -> Tuple[List, Dict]:
        # self.logger.root.setLevel(self.logger.DEBUG)
        self.data = data    
        self.logger = data["config_data"]["LOGGER"] if "LOGGER" in data["config_data"].keys() else logging
        self.logger.info("---------------------Inside REST FRAMEWORK------------------------")
        self.logger.info(f"-------Executing testcase - \"{self.data['config_data']['NAME']}\"---------")
        self.isLegacyPresent = self.isLegacyPresent()

        # set vars
        self.setVars()

        # setting reporter object
        self.reporter = Base(project_name=self.project, testcase_name=self.tcname)
        self.logger.info("--------------------Report object created ------------------------")
        self.reporter.addRow("Starting Test", f'Testcase Name: {self.tcname}', status.INFO) 

    def restEngine(self):
        output = []
        try:
            try:
                self.validateConf()
                self.run()
            except Exception as e:
                if str(e) == "abort":
                    self.logger.info("aborting execution")
                    # self.reporter.addMisc("REASON OF FAILURE","ABORTING EXECUTION")
                else:
                    self.logger.error(str(e))
                    traceback.print_exc()
                    self.logger.error(traceback.print_exc())
                    self.reporter.addMisc("REASON OF FAILURE", f"Something went wrong:- {str(e)}")
                    self.reporter.addRow("Executing Test steps", f'Something went wrong while executing the testcase- {str(e)}', status.ERR)
                    exceptiondata = traceback.format_exc().splitlines()
                    exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
                    self.reporter.addMisc("Reason of Failure",exceptionarray[0])

            VarReplacement(self).valueNotFound()
            output = writeToReport(self)
            return output, None
        except Exception as e:
            self.logger.error(traceback.print_exc())
            common.errorHandler(self.logger, e, "Error occured while running the testcas")
            error_dict = getError(e, self.data["config_data"])
            error_dict["json_data"] = self.reporter.serialize()
            return None, error_dict
    
    def run(self):
        self.getVals()
        # execute and format result
        self.execRequest()
        self.postProcess()
        MiscVariables(self).miscVariables()
        self.logger.info("--------------------Execution Completed ------------------------")
        self.reporter.finalizeReport()

    def validateConf(self):
        mandate = ["API", "METHOD"]
        self.list_subtestcases=[]
        self.request_obj=[]
        self.response_obj=[]
        if len(set(mandate) - set([i.upper() for i in self.data["config_data"].keys()])) > 0:
            # update REASON OF FAILURE in misc
            self.reporter.addMisc("REASON OF FAILURE", "Mandatory keys are missing")
            # self.reporter.addRow("Initiating Test steps", f'Error Occurred- Mandatory keys are missing', status.FAIL)
            raise Exception("mandatory keys missing")
     
        
        if(self.data["config_data"]["RUN_FLAG"]=="Y" and "SUBTESTCASES_DATA" in self.data["config_data"].keys()):
            # self.reporter.addRow("Parent Testcase",f'Testcase Name: {self.data["config_data"]["NAME"]}',status.INFO)
            self.list_subtestcases=self.data["config_data"]["SUBTESTCASES_DATA"]
            
            
            self.variables["local"] = {}
            self.variables["suite"] = self.data["SUITE_VARS"]
            self.parent_data=self.data["config_data"]
            for i in range(len(self.list_subtestcases)):
                self.reporter.addRow("<b>Subtestcase</b>",f'<b>Subtestcase Name: {self.list_subtestcases[i]["NAME"]}</b>',status.INFO)
                self.data["config_data"]=self.list_subtestcases[i]
                self.getVals()

                requestObj=api.Request()
                requestObj.api = self.api
                requestObj.method = self.method
                requestObj.body = self.body
                requestObj.headers = self.headers
                requestObj.file = self.file
                if self.auth_type == "NTLM":
                    requestObj.credentials = {"username": self.username, "password": self.password}
                    requestObj.auth = "PASSWORD"
                self.request_obj.append(requestObj)
              
                self.execRequest()
                
                self.postProcess()
                
                MiscVariables(self).miscVariables()
            del self.parent_data["SUBTESTCASES_DATA"]
            self.data["config_data"]=self.parent_data
            self.request_obj=[]

            
    # read config and get data
    def getVals(self):
        """This is a function to get the values from configData, store it in self object."""
        # capitalize the keys

        for k, v in self.data["config_data"].items():
            self.data.update({k.upper(): v})
        self.env = self.data.get("ENV", "PROD").strip(" ").upper()
        # get the api url
        if self.env not in self.data.keys():
            self.api = self.data["config_data"]["API"].strip(" ")
        else: 
            self.api = self.data.get(self.env, "PROD").strip(" ") + self.data["config_data"]["API"].strip(" ")
        
        # get the method
        self.method = self.data["config_data"].get("METHOD", "GET")

        # get the headers
        # self.headers = self.data["config_data"].get("HEADERS",{})
        self.headers = self.data["config_data"].get("HEADERS", {})
        

        #get miscellaneous variables for report.
        self.report_misc = self.data["config_data"].get("REPORT_MISC","")
        
        # get body
        self.body = self.data["config_data"].get("BODY", {})

        # get file
        self.file = self.data["config_data"].get("REQUEST_FILE", None)

        # get pre variables, not mandatory
        self.pre_variables = self.data["config_data"].get("PRE_VARIABLES", "")

        self.key_check = self.data["config_data"].get("KEY_CHECK", None)

        self.exp_status_code = self.getExpectedStatusCode("EXPECTED_STATUS_CODE") 

        self.post_assertion = self.data["config_data"].get("POST_ASSERTION", None)

        self.post_variables = self.data["config_data"].get("POST_VARIABLES", "")

        self.auth_type = self.data["config_data"].get("AUTHENTICATION", "")

        self.username = self.data["config_data"].get("USERNAME", self.data.get("USER", None))

        self.password = self.data["config_data"].get("PASSWORD", None)

        #get values of mandatory keys of legacy apis
        if self.isLegacyPresent and len(["LEGACY_API", "LEGACY_METHOD", "LEGACY_HEADERS", "LEGACY_BODY"] - self.data["config_data"].keys()) == 0:
            self.legacy_api = self.data["config_data"]["LEGACY_API"].strip(" ")
            self.legacy_method = self.data["config_data"].get("LEGACY_METHOD", "GET")
            self.legacy_headers = json.loads(str(self.data["config_data"].get("LEGACY_HEADERS", {})))
            self.legacy_body = json.loads(str(self.data["config_data"].get("LEGACY_BODY", {})))
            self.legacy_exp_status_code = self.getExpectedStatusCode("LEGACY_EXPECTED_STATUS_CODE")
            self.legacy_auth_type = self.data["config_data"].get("LEGACY_AUTHENTICATION", "")
        #setting variables and variable replacement
        
        PreVariables(self).preVariable()
        VarReplacement(self).variableReplacement()
        self.body=json.loads(self.body) if type(self.body) == str else self.body 
        self.headers=json.loads(self.headers) if type(self.headers) == str else self.headers 

    def file_upload(self,json_form_data): 
        files_data=[]
        json_form_data_1={}  
        for key,value in json_form_data.items():
            files_data_tuple=tuple()
            if(os.path.exists(json_form_data[key])):
                files_data_tuple+=(key,json_form_data[key])
            files_data.append(files_data_tuple)
        return files_data

    def execRequest(self):
        """This function
        -creates a request object, 
        -logs the request
        -runs before method
        -sends request
        -log response 
        -stores it in self object"""
        if(len(self.request_obj)>0):
            self.req_obj=self.request_obj[-1]
            
        else:
            self.req_obj = api.Request()
            # create request
            self.req_obj.api = self.api
            self.req_obj.method = self.method
            self.req_obj.body = self.body
            self.req_obj.headers = self.headers
            if(self.file is not None):
                self.req_obj.file = self.file_upload(json.loads(self.file))
            if self.auth_type == "NTLM":
                self.req_obj.credentials = {"username": self.username, "password": self.password}
                self.req_obj.auth = "PASSWORD"


    
        """legacy api request"""
        # create legacy request
        if hasattr(self,'legacy_api'):
            self.legacy_req = api.Request()
            self.legacy_req.api = self.legacy_api
            self.legacy_req.method = self.legacy_method
            self.legacy_req.headers = self.legacy_headers
            self.legacy_req.body = self.legacy_body  
        # calling the before method after creating the request object.
        self.beforeMethod()
        self.logRequest()
        # calling variable replacement after before method
        
        VarReplacement(self).variableReplacement()
       
        try:
            # raise Exception(f"Error occured while sending request- test")
            self.logger.info("--------------------Executing Request ------------------------")
            self.logger.info(f"url: {self.req_obj.api}")
            self.logger.info(f"method: {self.req_obj.method}")
            self.logger.info(f"request_body: {self.req_obj.body}")
            self.logger.info(f"headers: {self.req_obj.headers}") 

            # addig request misc
            self.reporter.addMisc("REQUEST URL", str(self.req_obj.api)) 
            self.reporter.addMisc("REQUEST METHOD", str(self.req_obj.method))
            self.reporter.addMisc("REQUEST BODY", str(self.req_obj.body))  # s3
            self.reporter.addMisc("REQUEST HEADERS", str(self.req_obj.headers))

            # execute request
            self.res_obj = api.Api().execute(self.req_obj)
            if(len(self.request_obj)>0):
                self.response_obj.append(self.res_obj)
            self.logger.info(f"API response code: {str(self.res_obj.status_code)}")

            # self.reporter.addMisc("RESPONSE BODY", str(self.res_obj.response_body))  # s3
            # self.reporter.addMisc("RESPONSE HEADERS", str(self.res_obj.response_headers))
            self.reporter.addMisc("ACTUAL/EXPECTED RESPONSE CODE", f"{self.res_obj.status_code}/{str(self.exp_status_code).strip('[]')}")

            # logging legacy api
            try:
                # if self.legacy_req is not None:
                self.logger.info("--------------------Executing legacy Request ------------------------")

                self.logger.info(f"legacy url: {self.legacy_req.api}")
                self.logger.info(f"legacy method: {self.legacy_req.method}")
                self.logger.info(f"legacy request_body: {self.legacy_req.body}")
                self.logger.info(f"legacy headers: {self.legacy_req.headers}")

                # addig request misc
                self.reporter.addMisc("LEGACY REQUEST URL", str(self.legacy_req.api))
                self.reporter.addMisc("LEGACY REQUEST METHOD", str(self.legacy_req.method))
                self.reporter.addMisc("LEGACY REQUEST BODY", str(self.legacy_req.body))  # s3
                self.reporter.addMisc("LEGACY REQUEST HEADERS", str(self.legacy_req.headers))

                self.legacy_res = api.Api().execute(self.legacy_req)

                # self.reporter.addMisc("LEGACY RESPONSE BODY", str(self.legacy_res.response_body))  # s3
                # self.reporter.addMisc("LEGACY RESPONSE HEADERS", str(self.legacy_res.response_headers))
                self.reporter.addMisc("ACTUAL/EXPECTED RESPONSE CODE", f"{self.legacy_res.status_code}/{str(self.legacy_exp_status_code).strip('[]')}")


                self.reporter.addMisc("Current Response Time", "{0:.{1}f} sec(s)".format(self.res_obj.response_time,2))
                self.reporter.addMisc("Legacy Response Time", "{0:.{1}f} sec(s)".format(self.legacy_res.response_time,2) )
                self.logResponse()
            except Exception as e:
                if not hasattr(self.legacy_res, "response_body"):
                    self.reporter.addMisc("Response Time", "{0:.{1}f} sec(s)".format(self.res_obj.response_time,2))
                    self.logResponse()
                elif str(e) == "abort":
                    raise Exception("abort")
                if self.isLegacyPresent:
                    traceback.print_exc()
        except Exception as e:
            if str(e) == "abort":
                raise Exception("abort")
            self.logger.info(traceback.print_exc())
            # self.reporter.addRow("Executing API", "Some error occurred while hitting the API", status.FAIL)
            self.reporter.addMisc("REASON OF FAILURE", f"Some error occurred while sending request- {str(e)}")
            raise Exception(f"Error occured while sending request - {str(e)}")

    def setVars(self):
        """
        For setting variables like testcase name, output folder etc.
        """
        self.default_report_path = os.path.join(os.getcwd(), "pyprest_reports")
        self.data["OUTPUT_FOLDER"] = self.data.get("OUTPUT_FOLDER", self.default_report_path)
        if self.data["OUTPUT_FOLDER"].strip(" ") == "":
            self.data["OUTPUT_FOLDER"] = self.default_report_path
        self.project = self.data["PROJECT_NAME"]
        self.tcname = self.data["config_data"]["NAME"]
        self.legacy_req = None
        self.req_obj = None
        self.res_obj = None
        self.legacy_res = None
        self.request_file = None
        self.env = self.data["ENV"]
        self.variables = {}
        self.category = self.data["config_data"].get("CATEGORY", None)
        # self.product_type = self.data["PRODUCT_TYPE"]

    def logRequest(self):
        if self.legacy_req is not None and self.legacy_req.api != '':
            self.logger.info(f"{self.legacy_req.__dict__}")
            self.logger.info(f"{self.req_obj.__dict__}")
            

            legacy_request_body = f"</br><b>REQUEST BODY</b>: {self.legacy_req.body}" if self.legacy_req.method.upper() != "GET" else ""
            current_request_body = f"</br><b>REQUEST BODY</b>: {self.req_obj.body}" if self.req_obj.method.upper() != "GET" else ""
                
            self.reporter.addRow("Executing the rest endpoint","Execution of base api and legacy api simultaneously",
                            status.INFO ,
                            CURRENT_API= f"<b>URL</b>: {self.req_obj.api}</br>" 
                             + f"<b>METHOD</b>: {self.req_obj.method}</br>" 
                             + f"<b>REQUEST HEADERS</b>: {self.req_obj.headers}" 
                             + current_request_body
                            ,LEGACY_API=f"<b>URL</b>: {self.legacy_req.api}</br>" 
                             + f"<b>METHOD</b>: {self.legacy_req.method}</br>" 
                             + f"<b>REQUEST HEADERS</b>: {self.legacy_req.headers}" 
                             + legacy_request_body
            )
        else:
            body_str = f"</br><b>REQUEST BODY</b>: {self.req_obj.body}" if self.req_obj.method.upper() != "GET" else ""
            self.reporter.addRow("Executing the REST Endpoint", 
                             f"<b>URL</b>: {self.req_obj.api}</br>" 
                             + f"<b>METHOD</b>: {self.req_obj.method}</br>" 
                             + f"<b>REQUEST HEADERS</b>: {self.req_obj.headers}" 
                             + body_str, 
                             status.PASS)

    def logResponse(self):
        if self.legacy_res is not None and self.legacy_req.api !='':
            legacy_response_body = self.legacy_res.response_body
            current_response_body = self.res_obj.response_body
            if isinstance(current_response_body, str):
                if "<!DOCTYPE html>" in current_response_body and "</html>" in current_response_body:
                    current_response_body = f"<a href={self.res_obj.api} target = '_blank'>Click here</a>"
            if isinstance(legacy_response_body,str):
                if "<!DOCTYPE html>" in legacy_response_body and "</html>" in legacy_response_body:
                    legacy_response_body = f"<a href={self.legacy_res.api} target = '_blank'>Click here</a>"            
            self.reporter.addRow("Details of the REST endpoint execution","Execution of Current and Legacy API simultaneously",
                            status.INFO ,
                            CURRENT_API= f"<b>CURRENT RESPONSE CODE</b>: {self.res_obj.status_code}</br>" 
                             + f"<b>CURRENT RESPONSE HEADERS</b>: {self.res_obj.response_headers}</br>" 
                             + f"<b>CURRENT RESPONSE BODY</b>:{current_response_body}",
                            LEGACY_API=f"<b>LEGACY STATUS CODE</b>: {self.legacy_res.status_code}</br>" 
                             + f"<b>LEGACY RESPONSE HEADERS</b>: {self.legacy_res.response_headers}</br>" 
                             + f"<b>LEGACY RESPONSE BODY</b>: {legacy_response_body}"
                             )
            if (self.legacy_res.status_code in self.legacy_exp_status_code) and (self.res_obj.status_code in self.exp_status_code) :
                self.reporter.addRow("Validating Response Code with Expected Status Codes", "Both status codes are matching with expected status codes",
                                status.PASS,
                                 CURRENT_API= f"<b>EXPECTED CURRENT RESPONSE CODE</b>: {str(self.exp_status_code).strip('[]')}</br>" 
                                 + f"<b>ACTUAL CURRENT RESPONSE CODE</b>: {str(self.res_obj.status_code)}", 
                                 LEGACY_API= f"<b>EXPECTED LEGACY RESPONSE CODE</b>: {str(self.legacy_exp_status_code).strip('[]')}</br>" 
                                 + f"<b>ACTUAL LEGACY RESPONSE CODE</b>: {str(self.legacy_res.status_code)}"
                                 )
            else:
                self.reporter.addRow("Validating Response Code with Expected Status Codes of both APIs", "Both status codes are not matching with expected status codes",
                                status.FAIL,
                                 CURRENT_API= f"<b>EXPECTED CURRENT RESPONSE CODE</b>: {str(self.exp_status_code).strip('[]')}</br>" 
                                 + f"<b>ACTUAL CURRENT RESPONSE CODE</b>: {str(self.res_obj.status_code)}", 
                                 LEGACY_API= f"<b>EXPECTED LEGACY RESPONSE CODE</b>: {str(self.legacy_exp_status_code).strip('[]')}</br>" 
                                 + f"<b>ACTUAL LEGACY RESPONSE CODE</b>: {str(self.legacy_res.status_code)}"
                                 )
                self.reporter.addMisc("REASON OF FAILURE", "Response code is not as expected")
                self.logger.info("status codes of both apis did not match, aborting testcase.....")
                raise Exception("abort")
                # raise Exception("abort")       
        else:
            body = self.res_obj.response_body
            if isinstance(body, str):
                if "<!DOCTYPE html>" in body and "</html>" in body:
                    body = f"<a href={self.req_obj.api} target = '_blank'>Click here</a>"
        
            self.reporter.addRow("Details of Request Execution", 
                                 f"<b>RESPONSE CODE</b>: {self.res_obj.status_code}</br>" 
                                 + f"<b>RESPONSE HEADERS</b>: {self.res_obj.response_headers}</br>" 
                                 + f"<b>RESPONSE BODY</b>: {str(body)}", 
                                 status.INFO)
            logging.info(f"<b>RESPONSE BODY</b>: {str(body)}")
            if self.res_obj.status_code in self.exp_status_code:
                self.reporter.addRow("Validating Response Code", 
                                 f"<b>EXPECTED RESPONSE CODE</b>: {str(self.exp_status_code).strip('[]')}</br>" 
                                 + f"<b>ACTUAL RESPONSE CODE</b>: {str(self.res_obj.status_code)}", 
                                 status.PASS)
            else:
                self.reporter.addRow("Validating Response Code", 
                                 f"<b>EXPECTED RESPONSE CODE</b>: {str(self.exp_status_code).strip('[]')}</br>" 
                                 + f"<b>ACTUAL RESPONSE CODE</b>: {str(self.res_obj.status_code)}", 
                                 status.FAIL)
                self.reporter.addMisc("REASON OF FAILURE", "Response code is not as expected")
                self.logger.info("status codes did not match, aborting testcase.....")
                raise Exception("abort")

    def postProcess(self):
        """To be run after API request is sent.
        It includes after method, post assertion and post vaiables"""

        PostVariables(self).postVariables()
        KeyCheck(self).keyCheck()
        PostAssertion(self).postAssertion()
        self.afterMethod()

    def beforeMethod(self):
        """This function
        -checks for the before file tag
        -stores package, module,class and method
        -runs before method if found
        -takes all the data from before method and updates the self object"""

        # check for before_file
        self.logger.info("CHECKING FOR BEFORE FILE___________________________")

        file_str = self.data["config_data"].get("BEFORE_FILE", "")
        if file_str == "" or file_str == " ":
            self.logger.info("BEFORE FILE NOT FOUND___________________________")
            self.reporter.addRow("Searching for pre API steps", "No Pre API steps found", status.INFO)

            return
        self.reporter.addRow("Searching for pre API steps", "Searching for before API steps", status.INFO)
        
        file_name = file_str.split("path=")[1].split(",")[0]
        if "CLASS=" in file_str.upper():
            class_name = file_str.split("class=")[1].split(",")[0]
        else:
            class_name = ""
        if "METHOD=" in file_str.upper():
            method_name = file_str.split("method=")[1].split(",")[0]
        else:
            method_name = "before"
        
        self.logger.info("Before file path:- " + file_name)
        self.logger.info("Before file class:- " + class_name)
        self.logger.info("Before file mthod:- " + method_name)
        try:
            # trying to download from s3 path
           
            if(file_name.__contains__('gem-np')):
                fileContent=download_from_s3(api=file_name,username=self.data.get("SUITE_VARS",None).get("username",None),bridge_token=self.data.get("SUITE_VARS",None).get("bridge_token",None))
                file_name = os.path.join(file_name.split(":")[-1])
                with open(file_name, "w+") as fp:
                    fp.seek(0)
                    fp.write(fileContent)
                    fp.truncate()
            #     before_file=file_name.split("/")
            #     folder = before_file[3:]
            #     my_bucket = before_file[2].split(".")[0]
            #     file = before_file[-1]
            #     file_name = custom_s3.download(bucket=my_bucket, file_name=file, folder=folder)
    
            file_obj = moduleImports(file_name)
            self.logger.info("Running before method")
            obj_ = file_obj
            before_obj = RestObj(
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
            self.extractObj(fin_obj)
            
        except Exception as e:
            self.logger.info(traceback.print_exc())
            self.reporter.addRow("Executing Before method", f"Some error occurred while searching for before method- {str(e)}", status.ERR)
        VarReplacement(self).variableReplacement()

    def afterMethod(self):
        """This function
        -checks for the after file tag
        -stores package, module,class and method
        -runs after method if found
        -takes all the data from after method and updates the self object"""

        self.logger.info("CHECKING FOR AFTER FILE___________________________")

        file_str = self.data["config_data"].get("AFTER_FILE", "")
        if file_str == "" or file_str == " ":
            self.logger.info("AFTER FILE NOT FOUND___________________________")
            self.reporter.addRow("Searching for post API steps", "No Post API steps found", status.INFO)
            return

        self.reporter.addRow("Searching for post API steps", "Searching for after method steps", status.INFO)
        
        file_name = file_str.split("path=")[1].split(",")[0]
        if "CLASS=" in file_str.upper():
            class_name = file_str.split("class=")[1].split(",")[0]
        else:
            class_name = ""
        if "METHOD=" in file_str.upper():
            method_name = file_str.split("method=")[1].split(",")[0]
        else:
            method_name = "after"
        self.logger.info("After file path:- " + file_name)
        self.logger.info("After file class:- " + class_name)
        self.logger.info("After file mthod:- " + method_name)
        try:
            if(file_name.__contains__('gem-np')):
                fileContent=download_from_s3(api=file_name,username=self.data["SUITE_VARS"].get("username",None),bridge_token=self.data["SUITE_VARS"].get("bridge_token",None))
                file_name = os.path.join(file_name.split(":")[-1])
                with open(file_name, "w+") as fp:
                    fp.seek(0)
                    fp.write(fileContent)
                    fp.truncate()
            # if(file_name.__contains__('s3')):
            #     after_file=file_name.split("/")
            #     folder = after_file[3:]
            #     my_bucket = after_file[2].split(".")[0]
            #     file = after_file[-1]
            #     file_name = custom_s3.download(bucket=my_bucket, file_name=file, folder=folder)
            file_obj = moduleImports(file_name)
            self.logger.info("Running before method")
            obj_ = file_obj
            after_obj = RestObj(
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
            self.extractObj(fin_obj)
        except Exception as e:
            self.reporter.addRow("Executing After method", f"Some error occurred while searching for after method- {str(e)}", status.ERR)

        VarReplacement(self).variableReplacement()
        pass

    def extractObj(self, obj):
        """To ofload the data from pyprest obj helper, assign the values back to self object"""

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

    def getExpectedStatusCode(self,exp_status_code_param):
        code_list = []
        # self.data["config_data"].get("EXPECTED_STATUS_CODE", 200)
        exp_status_code_string = self.data["config_data"].get(f"{exp_status_code_param}",str(200))
        if "," in exp_status_code_string:
            code_list = exp_status_code_string.strip('"').strip("'").split(",")
        elif "or" in exp_status_code_string.lower():
            code_list = exp_status_code_string.strip('"').strip("'").lower().split("or")
        else:
            code_list = [exp_status_code_string.strip("'").strip(" ").strip('"')]
        code_list = [int(each.strip(" ")) for each in code_list if each not in ["", " "]]
        return code_list
    
    def isLegacyPresent(self):
        if self.data["config_data"].get("LEGACY_API", None) is not None:
            if self.data["config_data"].get("LEGACY_METHOD", None) is not None:
                if json.loads(str(self.data["config_data"].get("LEGACY_HEADERS", {}))) is not None:
                        if json.loads(str(self.data["config_data"].get("LEGACY_BODY", {}))) is not None:
                            if self.getExpectedStatusCode("LEGACY_EXPECTED_STATUS_CODE") is not None:
                                if self.data["config_data"].get("LEGACY_AUTHENTICATION", "") is not None:
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        else:
                            return False
                else:
                    return False
            else:
                return False
        else:
            return False
    


   

