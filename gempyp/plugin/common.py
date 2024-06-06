from gempyp.engine.baseTemplate import TestcaseReporter
import glob, configparser, os, uuid, platform, tempfile, json, logging
from gempyp.libs.enums.status import status
from gempyp.engine.testData import TestData
from gempyp.engine.runner import getOutput
from gempyp.libs.logConfig import my_custom_logger, LoggingConfig
from gempyp.engine import dataUpload
from gempyp.libs.common import *
from datetime import datetime, timezone
from gempyp.libs.enums.status import status
import time

class Common:
    DATA = TestData()
    data = {}
    instance = None
    _dict = {}

    @classmethod
    def get_instance(self):
        testcase_name = "UI_Automation"
        # testcase_name = re.sub('[^A-Za-z0-9]+', '_', testcase_name)
        log_path = "ui_automation.txt"
        # if len(log_path) > 240:
        #     log_path = os.path.join(os.environ.get('TESTCASE_LOG_FOLDER'), str(uuid.uuid4()) +'.txt')
        self.logging = my_custom_logger(log_path)
        LoggingConfig(log_path)
        if self.instance is None:
            self.instance = Common()
        return self.instance


    def makeSuiteDetails(self, plugin_data:dict)->None:
            """
            this function will help to create suitedetails that will be used in sendSuiteData API
            plugin_data will be dictionary that holds the data from the hooks (in behave we are using it mainly for expectedTestcase count)
            this function is mainly picking data from .ini file(currently pytest.ini from root directory)
            """          

            try:  
                path = glob.glob(os.path.join('**','pytest.ini'),recursive=True)
                config = configparser.ConfigParser()
                config.read(path)
                self.dataFromIni = dict(config.items('pytest'))
                self.s_run_id = self.dataFromIni.get("project-name") + "_" + self.dataFromIni.get("environment","beta") + "_" + str(uuid.uuid4())
                self.dataFromIni['s-run-id'] = self.s_run_id
                run_mode = "LINUX_CLI"
                if os.name == 'nt':
                    run_mode = "WINDOWS"
                Suite_details = {
                    "s_run_id": self.dataFromIni["s-run-id"],
                    "s_start_time": datetime.now(timezone.utc),
                    "s_end_time": None,
                    "s_id": self.dataFromIni.get("S_ID", "test_id"),
                    "status": status.EXE.name,
                    "project_name": self.dataFromIni.get("project-name",""),
                    "report_name": self.dataFromIni.get("report-name","smoke_test"),
                    "run_type": "ON DEMAND",
                    "user": self.dataFromIni.get('jewel-user',None),
                    "env": self.dataFromIni.get("environment","beta"),
                    "machine": self.dataFromIni.get("machine",platform.node()),
                    "run_mode": run_mode,
                    "os": platform.system().upper(),
                    "meta_data": [],
                    "testcase_info": None,
                    "expected_testcases":plugin_data.get('expected-testcases',1),
                    "framework_name": "GEMPYP",
                }
                self.DATA.suite_detail = self.DATA.suite_detail.append(
                    Suite_details, ignore_index=True
                )
            except Exception:
                traceback.print_exc()


    def getTestcaseData(self, testcaseData:dict)->None:
            """
            this function is mainly to create testcase data 
            in this function we sending testcaseName key
            """
            try:
                self.jewel_user=False
                # global reporter
                self.reporter = TestcaseReporter(self.dataFromIni.get("project-name",""), testcaseData.get("testcaseName","Demo Test"))
                # reporter = TestcaseReporter(self.dataFromIni.get("project-name",""), testcaseData.get("testcaseName","Demo Test"))
                self.reporter.Status = status
                # reporter.Status = status
                projectName = self.dataFromIni.get("project-name","")
                env = self.dataFromIni.get("environment","beta")
                testcaseName = testcaseData.get("testcaseName","Demo Test")
                self.data["JEWEL_USER"] = self.dataFromIni.get('jewel-user',None)
                self.data["JEWEL_BRIDGE_TOKEN"] = self.dataFromIni.get("jewel-bridge-token")
                self.data["REPORT_LOCATION"] = self.dataFromIni.get("report-location")
                self.data["MACHINE"] = self.dataFromIni.get("machine",platform.node())
                self.data["MAIL_TO"] = self.dataFromIni.get("mail-to")
                self.data["MAIL_CC"] = self.dataFromIni.get("mail-cc")
                self.data["MAIL_BCC"] = self.dataFromIni.get("mail-bcc")
                self.data["ENTER_POINT"] = self.dataFromIni.get("enter-point")
                if self.data["JEWEL_USER"] and self.data["JEWEL_BRIDGE_TOKEN"]:
                    self.jewel_user=True
                report_type = self.data["REPORT_NAME"] = self.dataFromIni.get("report-name","Smoke Test")
                if not self.dataFromIni.get("s-run-id"):
                    self.data["s_run_id"] = self.s_run_id
                    os.environ["s_run_id"] = self.s_run_id
                else:
                    self.s_run_id = self.data["s_run_id"] = self.dataFromIni.get("s-run-id")
            except Exception:
                traceback.print_exc()

    def sendSuiteData(self):
        try:
            """this function is for calling first post api for suite data"""
            runBaseUrls(True,self.dataFromIni.get("enter-point"),self.dataFromIni.get("jewel-user"),self.dataFromIni.get("jewel-bridge-token"))
            dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.dataFromIni.get("jewel-bridge-token"), self.dataFromIni.get("jewel-user")) # check with deamon, should insert only once
        except Exception:
                traceback.print_exc()


    def send_testcase_data(self):
        try:
            # test_func_node = item.parent.obj
            output = []
            # global reporter
            self.reporter.finalizeReport()
            # reporter.finalizeReport()
            # create testcase self.reporter json
            # global reporter
            self.reporter.json_data = self.reporter.template_data.makeTestcaseReport()
            # reporter.json_data = reporter.template_data.makeTestcaseReport()
            # serializing data, adding suite data
            report_dict = self.reporter.serialize()
            # report_dict = reporter.serialize()
            report_dict["TESTCASEMETADATA"] = self.getMetaData()
            report_dict["config_data"] = self.getConfigData()
            # creating output json
            output.append(getOutput(report_dict))
            output[0]['testcase_dict']['run_type'], output[0]['testcase_dict']['run_mode'],output[0]['testcase_dict']['job_name'],output[0]['testcase_dict']['job_runid']="ON DEMAND","WINDOWS",None,None
            for i in output:
                i["testcase_dict"]["steps"] = i["json_data"]["steps"]
                dict_ = {}
                dict_["testcases"] = {}
                dict_["REPORT_LOCATION"] = os.getenv("REPORT_LOCATION")
                dict_["misc_data"] = {}
                # self.tmp_dir = os.path.join(tempfile.gettempdir(), self.data["s_run_id"] + ".txt")
                self.DATA.testcase_details = self.DATA.testcase_details.append(
                    i["testcase_dict"], ignore_index=True
                )   
                # self.self.DATA.testcaseDetails = pd.concat([self.self.DATA.testcaseDetails, pd.DataFrame(list(i["testcase_dict"].items()))])
                self.updateTestcaseMiscData(i["misc"], tc_run_id=i["testcase_dict"].get("tc_run_id"))
                suite_data = self.DATA.getJSONData()
                if isinstance(suite_data, str):
                    suite_data = json.loads(suite_data)
                if len(self._dict)==0:
                    dict_[self.s_run_id] = self.updateSuiteData(suite_data)
                    dict_["testcases"][i["testcase_dict"].get("tc_run_id")] = i["json_data"]
                    self._dict = dict_
                else:
                    self._dict["s_run_id"] = self.updateSuiteData(suite_data,self._dict[self.s_run_id])
                    self._dict["testcases"][i["testcase_dict"].get("tc_run_id")] = i["json_data"]
                updatedData=json.loads(self.DATA.totestcaseJson(i["testcase_dict"]["tc_run_id"].upper(), self.data["s_run_id"]))
                logging.info("TC_RUN_ID : "+i["testcase_dict"]["tc_run_id"].upper())
                dataUpload.sendTestcaseData(json.dumps(updatedData), self.data["JEWEL_BRIDGE_TOKEN"], self.data["JEWEL_USER"])  # instead of output, I need to pass s_run id and  tc_run_id
                
        except Exception:
            traceback.print_exc()

    def getMetaData(self):
        try:
            data = {
                'PROJECT_NAME': self.dataFromIni.get("project-name",""), 
                'ENVIRONMENT': self.dataFromIni.get("environment",""), 
                's_run_id': self.dataFromIni.get("s-run-id",""), 
                'USER': self.dataFromIni.get("jewel-user",""), 
                'MACHINE': self.dataFromIni.get("machine",platform.node()), 
                'REPORT_LOCATION': self.dataFromIni.get("report-location",""),
                'SUITE_VARS': self.dataFromIni.get("suite-vars", {}),
                'INVOKE_USER': os.getenv("INVOKEUSER", self.data["JEWEL_USER"])}
            return data
        except Exception:
            traceback.print_exc()


    def getConfigData(self):
        try:
            data = {'NAME': self.dataFromIni["project-name"], 'CATEGORY': 'External','LOGGER': ""}
            return data
        except Exception:
            traceback.print_exc()

    def updateTestcaseMiscData(self, misc, tc_run_id):
            
        try:
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
        except Exception:
            traceback.print_exc()


    def updateSuiteData(self, current_data, old_data=None):
        try:
            """
            updates the suiteData after all the runs have been executed
            """
            
            start_time = current_data["suits_details"]["s_start_time"]
            end_time = current_data["suits_details"]['testcase_details'][-1]["end_time"]
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
        except Exception:
            traceback.print_exc()
    
    def createReport(self):
        
        try:    
            json_data = self._dict[self.s_run_id]
            jewel= self.jewel_user
            bridgetoken=self.dataFromIni.get("jewel-bridge-token")
            testcaseData = self._dict["testcases"]
            suite_data = json_data["suits_details"]
            suite_data["misc_data"] = self._dict["misc_data"]
            username = suite_data["user"]
            del suite_data["testcase_details"]
            del suite_data["testcase_info"]
            response_code = dataUpload.sendSuiteData(json.dumps(suite_data), bridgetoken, username, mode="PUT")
            if response_code in [200,201]:
                jewelLink = DefaultSettings.getUrls('jewel-url')
                if jewelLink is not None:
                    # jewel_link = f'{jewelLink}/#/autolytics/execution-report?s_run_id={self.s_run_id}&p_id={DefaultSettings.project_id}'
                    jewel_link = f'{jewelLink}/#/autolytics/execution-report?s_run_id={self.s_run_id}'
                    logging.info(f"Jewel link of gempyp report - {jewel_link}")
            else:
                logging.info("Some error occurred while uploading data")
        except Exception:
            traceback.print_exc()
    

common = Common.get_instance()