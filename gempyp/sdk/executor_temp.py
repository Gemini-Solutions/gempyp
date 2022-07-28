from ast import Suite
import getpass
import json
from pathlib import Path
import sys
import uuid
from datetime import datetime
from gempyp.engine.baseTemplate import testcaseReporter
from gempyp.engine.runner import getOutput
from gempyp.engine.testData import testData
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


class Executor(testcaseReporter):
    def __init__(self):
        self.log_file = tempfile.gettempdir() + "logs.log"
        sys.stdout = sys.stderr =  open(self.log_file, 'w')
        self.data = self.getTestcaseData()
        self.makeOutputFolder()
        self.reporter = testcaseReporter(self.data["PROJECT"], self.data["NAME"])

        path = __file__
        path = path.rsplit(os.sep, 1)[0]
        if not os.getenv("PID"):
            os.environ["PID"] = str(os.getpid())
            subprocess.Popen([os.environ["_"], os.path.join(path, "worker.py")], shell=True)
        self.DATA = testData()
        # make suite details and upload it
        self.makeSuiteDetails()

        try:
            dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.data["BRIDGETOKEN"], self.data["USERNAME"]) # check with deamon, should insert only once
            
            logging.info("Suite data inserted")  # logging not working
        except Exception as e:
            print('ignore exception')
            pass

    def __del__(self):
        self.final()

    def final(self):       
        output = []
        
        # destructor of reporter object called
        self.reporter.finalize_report()
        
        # create testcase reporter json
        self.reporter.jsonData = self.reporter.templateData.makeTestcaseReport("" ,"")
        # serializing data, adding suite data
        reportDict = self.reporter.serialize()

        reportDict["TESTCASEMETADATA"] = self.getMetaData()
        reportDict["configData"] = self.getConfigData()

        # creating output json
        output.append(getOutput(reportDict))
        for i in output:
            i["testcaseDict"]["steps"] = i["jsonData"]["steps"]
            dict_ = {}
            dict_["testcases"] = {}
            dict_["OUTPUT_FOLDER"] = self.ouput_folder
            tmp_dir = os.path.join(tempfile.gettempdir(), self.s_run_id + ".txt")

            self.DATA.testcaseDetails = self.DATA.testcaseDetails.append(
                i["testcaseDict"], ignore_index=True
            )
            # self.DATA.testcaseDetails = pd.concat([self.DATA.testcaseDetails, pd.DataFrame(list(i["testcaseDict"].items()))])
            self.updateTestcaseMiscData(i["misc"], tc_run_id=i["testcaseDict"].get("tc_run_id"))
            suite_data = self.DATA.getJSONData()
            if isinstance(suite_data, str):
                suite_data = json.loads(suite_data)
            if not os.path.exists(tmp_dir):
                with open(tmp_dir, "w") as f:
                    dict_[self.s_run_id] = self.updateSuiteData(suite_data)
                    dict_["testcases"][i["testcaseDict"].get("tc_run_id")] = i["jsonData"]
                    f.write(json.dumps(dict_))
            else:
                with open(tmp_dir, "r+") as f:
                    data = f.read()
                    data = json.loads(data)
                    data[self.s_run_id] = self.updateSuiteData(suite_data, data[self.s_run_id])
                    data["testcases"][i["testcaseDict"].get("tc_run_id")] = i["jsonData"]
                    f.seek(0)
                    f.write(json.dumps(data))
                    # start time and endtime are null

            dataUpload.sendTestcaseData((self.DATA.totestcaseJson(i["testcaseDict"]["tc_run_id"].upper(), self.data["S_RUN_ID"])), self.data["BRIDGETOKEN"], self.data["USERNAME"])  # instead of output, I need to pass s_run id and  tc_run_id
            sys.stdout.close()
            os.rename(self.log_file, tmp_dir.split(".")[0] + "log")

    def getTestcaseData(self):
        config_file = configparser.ConfigParser()
        directory_path = os.getcwd()
        if not os.path.exists(directory_path + os.sep + "gempyp.conf"):
            print("Config file is missing. Aborting  gempyp report......")
            sys.exit()
        config_file.read("gempyp.conf")
        data = {}
        self.projectName = data["PROJECT"] = config_file['ReportSetting']["project"]
        self.testcaseName = data["NAME"] = self.getMethodName()
        self.env = data["ENV"] = config_file['ReportSetting'].get("env", "PROD")
        data["USERNAME"] = config_file['ReportSetting'].get("username", getpass.getuser())
        data["BRIDGETOKEN"] = config_file['ReportSetting'].get("bridgetoken", None)
        data["OUTPUT_FOLDER"] = config_file['ReportSetting'].get("outputfolder", None)
        data["MACHINE"] = platform.node()
        data["MAIL"] = config_file['ReportSetting'].get("mail", None)
        self.report_type = data["REPORT_TYPE"] = config_file['ReportSetting'].get("reportname", "SMOKE_TEST")
        if not os.getenv("S_RUN_ID"):
            s_run_id = data["PROJECT"] + "_" + data["ENV"] + "_" + str(uuid.uuid4())
            os.environ["S_RUN_ID"] = s_run_id.upper()
        self.s_run_id = data["S_RUN_ID"] = config_file['ReportSetting'].get("s_run_id", os.getenv("S_RUN_ID"))
        return data

    def getMetaData(self):
        data = {
            'PROJECTNAME': self.data["PROJECT"], 
            'ENV': self.data["ENV"], 
            'S_RUN_ID': self.data["S_RUN_ID"], 
            'USER': self.data["USERNAME"], 
            'MACHINE': self.data["MACHINE"], 
            'OUTPUT_FOLDER': self.data["OUTPUT_FOLDER"]}
        return data

    def getMethodName(self):
        try:
            currframe = inspect.currentframe()
            callframe = inspect.getouterframes(currframe, 2)
            count = -1
            while count < 0:
                if callframe[count][3] != '<module>':
                    method = callframe[count][3]
                    filename = callframe[count][1].split(os.sep)[-1].split(".")[0]
                    method = callframe[count][3] + "_" + filename
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
        SuiteDetails = {
            "s_run_id": self.data["S_RUN_ID"],
            "s_start_time": datetime.now(timezone.utc),
            "s_end_time": None,
            "status": status.EXE.name,
            "project_name": self.data["PROJECT"],
            "run_type": "ON DEMAND",
            "report_type": self.data["REPORT_TYPE"],
            "user": self.data["USERNAME"],
            "env": self.data["ENV"],
            "machine": self.data["MACHINE"],
            "initiated_by": self.data["USERNAME"],
            "run_mode": run_mode,
        }
        self.DATA.suiteDetail = self.DATA.suiteDetail.append(
            SuiteDetails, ignore_index=True
        )
        # self.DATA.suiteDetail = pd.concat([self.DATA.suiteDetail, pd.DataFrame(list(SuiteDetails.items()))])

        

    def updateTestcaseMiscData(self, misc, tc_run_id):
        """
        updates the misc data for the testcases
        """
        miscList = []

        for miscData in misc:
            temp = {}
            # storing all the key in upper so that no duplicate data is stored
            temp["key"] = miscData.upper()
            temp["value"] = misc[miscData]
            temp["run_id"] = tc_run_id
            temp["table_type"] = "TESTCASE"
            miscList.append(temp)

        self.DATA.miscDetails = self.DATA.miscDetails.append(
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
        if self.data.get("OUTPUT_FOLDER"):
            self.ouput_folder = os.path.join(
                self.data.get("OUTPUT_FOLDER"), report_folder_name
            )
        else:
            home = str(Path.home())
            self.ouput_folder = os.path.join(
                home, "gempyp_reports", report_folder_name
            )

        os.makedirs(self.ouput_folder)

    def updateSuiteData(self, current_data, old_data=None):
        """
        updates the suiteData after all the runs have been executed
        """
        start_time = current_data["Suite_Details"]["s_start_time"]
        end_time = current_data["Suite_Details"]["TestCase_Details"][0]["end_time"]
        testcaseData = current_data["Suite_Details"]["TestCase_Details"]
        if old_data:
            testcaseData = (old_data["Suite_Details"]["TestCase_Details"]
             + current_data["Suite_Details"]["TestCase_Details"])
            start_time = old_data["Suite_Details"]["s_start_time"]
        statusDict = {k.name: 0 for k in status}
        for i in testcaseData:
            statusDict[i["status"]] += 1
        # get the status count of the status
        SuiteStatus = status.FAIL.name

        # based on the status priority
        for s in status:
            if statusDict.get(s.name, 0) > 0:
                SuiteStatus = s.name

        current_data["Suite_Details"]["status"] = SuiteStatus
        current_data["Suite_Details"]["TestCase_Details"] = testcaseData
        current_data["Suite_Details"]["s_start_time"] = start_time
        current_data["Suite_Details"]["s_end_time"] = end_time
        count = 0
        for key in list(statusDict.keys()):
            if statusDict[key] == 0:
                del statusDict[key]
            else:
                count += statusDict[key]
        statusDict["Total"] = count
        current_data["Suite_Details"]["Testcase_Info"] = statusDict

        return current_data
