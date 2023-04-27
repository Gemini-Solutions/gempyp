import getpass
import json
from pathlib import Path
import sys
import uuid
from datetime import datetime
from gempyp.engine.baseTemplate import TestcaseReporter
from gempyp.engine.runner import getOutput
from gempyp.engine.testData import TestData
from gempyp.engine import dataUpload
import configparser
import inspect
from datetime import timezone
import platform
import logging
import tempfile
import subprocess
import sys
import os
import pandas as pd
from gempyp.libs.enums.status import status
from gempyp.libs.common import *


class Executor(TestcaseReporter):
    def __init__(self, **kwargs):
        self.method = kwargs.get("tc_name", self.getMethodName())
        self.log_file = tempfile.gettempdir() + "\logs.log"
        # os.makedirs("testcase_log_folder")
        print(self.log_file)
        sys.stdout = sys.stderr =  open(self.log_file, 'w')
        logging.basicConfig(filename="logs.log", filemode='w', format='%(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
        # custom_logger = my_custom_logger("logs.log")
        logging.info("inside constructor here--------------------")
        logging.info(f"-------Executing testcase - {self.getMethodName()}---------")
        self.data = self.getTestcaseData()
        self.reporter = TestcaseReporter(self.data["PROJECT_NAME"], self.data["NAME"])
       
        

        path = __file__
        path = path.rsplit(os.sep, 1)[0]
        self.DATA = TestData()
        # make suite details and upload it
        self.makeSuiteDetails()
        runBaseUrls(self.jewel_user,self.data["ENTER_POINT"],self.data["JEWEL_USER"],self.data["JEWEL_BRIDGE_TOKEN"])
        if not os.getenv("PID"):
            self.makeOutputFolder()
            os.environ["PID"] = str(os.getpid())
            subprocess.Popen([sys.executable, os.path.join(path, "worker.py")], shell=True)
            try:
                logging.info(f"---------------S_RUN_ID-------------{self.s_run_id}")
                dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.data["JEWEL_BRIDGE_TOKEN"], self.data["JEWEL_USER"]) # check with deamon, should insert only once
                  # logging not working
            except Exception as e:
                print(f"Exception occured - {e}")
                pass

    def __del__(self):
        self.final()

    def final(self):       
        output = []
        
        # destructor of reporter object called
        
        self.reporter.finalizeReport()
        
        # create testcase reporter json
        self.reporter.json_data = self.reporter.template_data.makeTestcaseReport()
        # serializing data, adding suite data
        report_dict = self.reporter.serialize()

        report_dict["TESTCASEMETADATA"] = self.getMetaData()
        report_dict["config_data"] = self.getConfigData()
        # creating output json
        output.append(getOutput(report_dict))
        for i in output:
            i["testcase_dict"]["steps"] = i["json_data"]["steps"]
            dict_ = {}
            dict_["testcases"] = {}
            dict_["REPORT_LOCATION"] = os.getenv("REPORT_LOCATION")
            dict_["misc_data"] = {}
            tmp_dir = os.path.join(tempfile.gettempdir(), self.s_run_id + ".txt")
            

            self.DATA.testcase_details = self.DATA.testcase_details.append(
                i["testcase_dict"], ignore_index=True
            )
            # self.DATA.testcaseDetails = pd.concat([self.DATA.testcaseDetails, pd.DataFrame(list(i["testcase_dict"].items()))])
            self.updateTestcaseMiscData(i["misc"], tc_run_id=i["testcase_dict"].get("tc_run_id"))
            suite_data = self.DATA.getJSONData()
            if isinstance(suite_data, str):
                suite_data = json.loads(suite_data)
            if isinstance(self.DATA.toSuiteJson(), str):
                suite_temp = json.loads(self.DATA.toSuiteJson())
            if not os.path.exists(tmp_dir):
                with open(tmp_dir, "w") as f:
                    dict_[self.s_run_id] = self.updateSuiteData(suite_data)
                    dict_["testcases"][i["testcase_dict"].get("tc_run_id")] = i["json_data"]
                    f.write(json.dumps(dict_))
            else:
                with open(tmp_dir, "r+") as f:
                    data = f.read()
                    data = json.loads(data)
                    data[self.s_run_id] = self.updateSuiteData(suite_data, data[self.s_run_id])
                    data["testcases"][i["testcase_dict"].get("tc_run_id")] = i["json_data"]
                    f.seek(0)
                    f.write(json.dumps(data))
            logging.info("---------------TC_RUN_ID-----------------"+i["testcase_dict"]["tc_run_id"].upper())
            dataUpload.sendTestcaseData((self.DATA.totestcaseJson(i["testcase_dict"]["tc_run_id"].upper(), self.data["S_RUN_ID"])), self.data["JEWEL_BRIDGE_TOKEN"], self.data["JEWEL_USER"])  # instead of output, I need to pass s_run id and  tc_run_id
            
            # sys.stdout.close()
        
            # os.rename(self.log_file, tmp_dir.rsplit(".", 1)[0] + ".log")

            

    def getTestcaseData(self):
        self.jewel_user=False
        config_file = configparser.ConfigParser()
        directory_path = os.getcwd()

        if not os.path.exists(directory_path + os.sep + "gempyp.conf"):
            print("Config file is missing. Aborting  gempyp report......")
            sys.exit()
        config_file.read("gempyp.conf")
        data = {}
        self.projectName = data["PROJECT_NAME"] = config_file['ReportSetting']["project_name"]
        self.testcaseName = data["NAME"] = self.method
        self.env = data["ENVIRONMENT"] = config_file['ReportSetting'].get("environment", "PROD")
        data["JEWEL_USER"] = config_file['ReportSetting'].get("jewel_user", getpass.getuser())
        data["JEWEL_BRIDGE_TOKEN"] = config_file['ReportSetting'].get("jewel_bridge_token", None)
        data["REPORT_LOCATION"] = config_file['ReportSetting'].get("report_location", None)
        data["MACHINE"] = platform.node()
        data["MAIL_TO"] = config_file['ReportSetting'].get("mail_to", None)
        data["MAIL_CC"] = config_file['ReportSetting'].get("mail_cc", None)
        data["MAIL_BCC"] = config_file['ReportSetting'].get("mail_bcc", None)
        data["ENTER_POINT"]=config_file['ReportSetting'].get("enter_point", None)
        if data["JEWEL_USER"] and data["JEWEL_BRIDGE_TOKEN"]:
            self.jewel_user=True
        self.report_type = data["REPORT_NAME"] = config_file['ReportSetting'].get("report_name", "SMOKE_TEST")
        if not os.getenv("S_RUN_ID"):
            s_run_id = data["PROJECT_NAME"] + "_" + data["ENVIRONMENT"] + "_" + str(uuid.uuid4())
            os.environ["S_RUN_ID"] = s_run_id.upper()
        self.s_run_id = data["S_RUN_ID"] = config_file['ReportSetting'].get("s_run_id", os.getenv("S_RUN_ID"))
        return data

    def getMetaData(self):
        data = {
            'PROJECT_NAME': self.data["PROJECT_NAME"], 
            'ENVIRONMENT': self.data["ENVIRONMENT"], 
            'S_RUN_ID': self.data["S_RUN_ID"], 
            'USER': self.data["JEWEL_USER"], 
            'MACHINE': self.data["MACHINE"], 
            'REPORT_LOCATION': self.data["REPORT_LOCATION"],
            'SUITE_VARS': self.data.get("SUITE_VARS", {}),
            'INVOKE_USER': os.getenv("INVOKEUSER", self.data["JEWEL_USER"])}
        return data

    def getMethodName(self):
        try:
            currframe = inspect.currentframe()
            callframe = inspect.getouterframes(currframe, 2)
            count = -1
            while count < 0:
                if callframe[2][3] != '<module>':
                    # method = callframe[2][3]
                    filename = callframe[2][1].split(os.sep)[-1].split(".")[0]
                    method = callframe[2][3] + "_" + filename
                    break
                count = (count - 1)%(-len(callframe))
        except Exception as e:
            print(e)
            method = f"Method_{str(uuid.uuid4())}"
        return method

    def getConfigData(self):
        data = {'NAME': self.data["NAME"], 'CATEGORY': 'External','LOGGER': ""}
        return data

    def makeSuiteDetails(self):
        """
        making suite Details 
        """
        
        run_mode = "LINUX_CLI"
        if os.name == 'nt':
            run_mode = "WINDOWS"
        Suite_details = {
            "s_run_id": self.data["S_RUN_ID"],
            "s_start_time": datetime.now(timezone.utc),
            "s_end_time": None,
            "s_id": self.data.get("S_ID", "test_id"),
            "status": status.EXE.name,
            "project_name": self.data["PROJECT_NAME"],
            "report_name": self.data["REPORT_NAME"],
            "run_type": "ON DEMAND",
            "user": self.data["JEWEL_USER"],
            "env": self.data["ENVIRONMENT"],
            "machine": self.data["MACHINE"],
            "initiated_by": self.data["JEWEL_USER"],
            "run_mode": run_mode,
            "os": platform.system().upper(),
            "meta_data": [],
            "testcase_info": None,
            "expected_testcases":2,
            "framework_name": "GEMPYP",
        }
        self.DATA.suite_detail = self.DATA.suite_detail.append(
            Suite_details, ignore_index=True
        )

        

    def updateTestcaseMiscData(self, misc, tc_run_id):
        """
        updates the misc data for the testcases
        """
        miscList = []

        for misc_data in misc:
            temp = {}
            # storing all the key in upper so that no duplicate data is stored
            temp["key"] = misc_data.upper()
            temp["value"] = misc[misc_data]
            temp["run_id"] = tc_run_id
            temp["table_type"] = "TESTCASE"
            miscList.append(temp)

        self.DATA.misc_details = self.DATA.misc_details.append(
            miscList, ignore_index=True
        )

    def makeOutputFolder(self):
        """
        to make GemPyp_Report folder 
        """

        logging.info("---------- Making output folders -------------")
        report_folder_name = f"{self.projectName}_{self.env}"
        if self.report_type:
            report_folder_name = report_folder_name + f"_{self.report_type}"
        date = datetime.now().strftime("%Y_%b_%d_%H%M%S_%f")
        report_folder_name = report_folder_name + f"_{date}"
        if self.data.get("REPORT_LOCATION"):
            self.ouput_folder = os.path.join(
                self.data.get("REPORT_LOCATION"), report_folder_name
            )
        else:
            home = str(Path.home())
            self.ouput_folder = os.path.join(
                home, "gempyp_reports", report_folder_name
            )
        os.environ["REPORT_LOCATION"] = self.ouput_folder

        os.makedirs(self.ouput_folder)

    def updateSuiteData(self, current_data, old_data=None):
        """
        updates the suiteData after all the runs have been executed
        """
        start_time = current_data["suits_details"]["s_start_time"]
        end_time = current_data["suits_details"]['testcase_details'][0]["end_time"]
        testcaseData = current_data["suits_details"]['testcase_details']
        if old_data:
            testcaseData = (old_data["suits_details"]['testcase_details']
             + current_data["suits_details"]['testcase_details'])
            start_time = old_data["suits_details"]["s_start_time"]
        statusDict = {k.name: 0 for k in status}
        for i in testcaseData:
            statusDict[i["status"]] += 1
        # get the status count of the status
        SuiteStatus = status.FAIL.name

        # based on the status priority
        for s in status:
            if statusDict.get(s.name, 0) > 0:
                SuiteStatus = s.name

        current_data["suits_details"]["status"] = SuiteStatus
        current_data["suits_details"]['testcase_details'] = testcaseData
        current_data["suits_details"]["s_start_time"] = start_time
        current_data["suits_details"]["s_end_time"] = end_time
        count = 0
        for key in list(statusDict.keys()):
            if statusDict[key] == 0:
                del statusDict[key]
            else:
                count += statusDict[key]
        statusDict["total"] = count
        current_data["suits_details"]["expected_testcases"]=count
        current_data["suits_details"]["testcase_info"] = statusDict

        return current_data