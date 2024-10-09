import pandas as pd
import traceback
import json
from gempyp.libs.common import dateTimeEncoder, findDuration
from datetime import datetime, timezone
import numpy as np
from gempyp.engine import dataUpload
import logging
import os
from gempyp.config import DefaultSettings
from cryptography.fernet import Fernet
from gempyp.config.DefaultSettings import encrypt_key, checkUrl

class TestData:
    def __init__(self):
        """
        declairing some attribute the are used in testcaseDetails in report and return a object that is used to update data
        """
        self.testcaseDetailColumn = [
            "tc_run_id",
            "start_time",
            "end_time",
            "name",
            "category",
            "log_file",
            "status",
            "steps",
            "machine",
            "result_file",
            "product_type",
            "ignore",
            "meta_data",
            "user_defined_data",
            "base_user",
            "invoke_user",
            "run_type",
            "run_mode"
        ]
        self.misc_detail_column = ["run_id", "key", "value", "table_type"]

        # can have anyamount of columns
        # this should always have one row so it can be made a dict or something instad of a dataframe
        self.suite_detail = pd.DataFrame()

        self.testcase_details = pd.DataFrame(columns=self.testcaseDetailColumn)
        self.misc_details = pd.DataFrame(columns=self.misc_detail_column)

    def toSuiteJson(self):
        """
        converts the dataframe to Json
        used in uploadsuitedata (run() method in engine.py)
        """
        if self.suite_detail.empty:
            return {}
        
        self.suite_detail = self.suite_detail.replace(np.nan, '-', regex=True)
        data = self.suite_detail.to_dict(orient="records")[0]
        misc_data = self.misc_details[
            self.misc_details["table_type"].str.upper() == "SUITE"
        ]
        # the above misc data is not being used

        data["meta_data"] = data["meta_data"]
        return json.dumps(data, cls=dateTimeEncoder)

    def totestcaseJson(self, tc_run_id, s_run_id):
        """
        returns the json for testcasedata
        used in update_df method of engine.py
        """

        self.testcase_details = self.testcase_details.replace(np.nan, '-', regex=True)
        test_data = self.testcase_details.loc[
            self.testcase_details["tc_run_id"].str.upper() == tc_run_id
        ]
        if test_data.empty:
            return {}
        test_data = test_data.to_dict(orient="records")[0]
        misc_data = self.misc_details.loc[self.misc_details["run_id"].str.upper() == tc_run_id]
        misc_data = misc_data.to_dict(orient="records")
        test_status = {}
        for step in test_data["steps"]:
            key = step.get("status")
            if test_status.get(key, None) is not None:
                test_status[key] = test_status.get(key) + 1
            else:
                test_status[key] = 1
        test_status["TOTAL"] = sum(test_status.values())
        prio_list = ['TOTAL', 'PASS', 'FAIL']
        sorted_dict = {}
        for key in prio_list:
            if key in test_status:
                sorted_dict[key] = test_status[key]
                test_status.pop(key)
            elif key == "PASS" or key == 'FAIL':
                sorted_dict[key] = 0
        sorted_dict.update(test_status)
        # test_data["duration"] = findDuration(test_data["start_time"], test_data["end_time"])

        test_data["user_defined_data"] = dict()
        # test_data["duration"]="{0:.{1}f} sec(s)".format((test_data["end_time"]-test_data["start_time"]).total_seconds(),2)
        """ Adding misc data to user_defined_data column for each testcase
        Here misc data is only for one testcase.
        {"key1": "value1", "key2": "value2"...}"""
        if len(misc_data) > 0:
            for miscs in misc_data:
                # logging.info("--- misc key", miscs.get("key", None))
                key = str(miscs["key"])
                val = str(miscs["value"])
                test_data["user_defined_data"][key] = val

        meta_data = [
            {
                "TESTCASE NAME": test_data["name"], 
                "SERVICE PROJECT": "None", 
                "DATE OF EXECUTION": {"value": datetime.now(timezone.utc), "type": "date"},
                # "RESPONSE TIME":"{0:.{1}f} sec(s)".format((test_data["end_time"]-test_data["start_time"]).total_seconds(),2)
            }, 
            {
                "EXECUTION STARTED ON": {"value": test_data["start_time"], "type": "datetime"},
                "EXECUTION ENDED ON": {"value": test_data["end_time"], "type": "datetime"}, 
                "EXECUTION DURATION": findDuration(test_data["start_time"], test_data["end_time"])
            }, 
            sorted_dict
            # {"response_time":"{0:.{1}f} sec(s)".format((test_data["end_time"]-test_data["start_time"]).total_seconds(),2)}
            ]

        test_data["meta_data"] = meta_data
        test_data["s_run_id"] = s_run_id
        test_data["user_defined_data"]["duration"]="{0:.{1}f} sec(s)".format((test_data["end_time"]-test_data["start_time"]).total_seconds(),2)
        if(test_data.get("testcase_id", None) is not None):
            test_data["testcase_id"]=int(test_data["testcase_id"])
        testcase_type = None

        if("GEMPYP" == test_data["product_type"]):
            testcase_type = "GEMPYP"
        elif("GEMPYP-PR" == test_data["product_type"]):
            testcase_type = "PYPREST"
        elif("GEMPYP-DV" == test_data["product_type"]):
            testcase_type = "DV"
        else:
            testcase_type = "DV-API"
        
        test_data["type"] = testcase_type
        return json.dumps(test_data, cls=dateTimeEncoder)

    def _validate(self):
        """
        used by fromJSON to validate the json data
        """
        pass

    def getJSONData(self):
        """
        provide the report json to makereport() method of engine file
        """
        suite_report = {}
        self.suite_detail = self.suite_detail.replace(np.nan, "-", regex=True)
        suite_dict = self.suite_detail.to_dict(orient="records")[0]
        testcase_dict = self.testcase_details.to_dict(orient="records")
        misc_dict = self.misc_details.to_dict(orient="records")
        try:

            # converting testcase_dict to dict for easy parsing
            test_dict = {d['tc_run_id']: d for d in testcase_dict}
            key = list(test_dict.keys())
            key = key[0]
            test_data = test_dict[key]
            test_dict[key] = test_data
            for each_misc in misc_dict:
                test_dict[each_misc['run_id']][each_misc["key"]] = each_misc["value"]

            # converting dict back to list
            testcase_dict = [test_dict[tc_run_id] for tc_run_id in test_dict.keys()]
        except Exception as e:
            traceback.print_exc()

        # print(testcase_dict, "++++++++++++++++++++++++++++++++++++++++")
        for i in range(len(testcase_dict)):
            for key in ["meta_data", "base_user", "invoke_user", "user_defined_data","LOG_FILE"]:
                if(key in testcase_dict[i].keys()):
                    testcase_dict[i].pop(key)
        suite_dict["testcase_details"] = testcase_dict
        testcase_counts = self.getTestcaseCounts()

        prio_list = ['total', 'PASS', 'FAIL']  # to be optimized
        sorted_dict = {}
        for key in prio_list:
            if key in testcase_counts :
                sorted_dict[key] = testcase_counts[key]
                testcase_counts.pop(key)
            elif key == "PASS" or key == 'FAIL':
                sorted_dict[key] = 0
        sorted_dict.update(testcase_counts)
        testcase_counts = sorted_dict
        suite_dict["testcase_info"] = testcase_counts
        suite_report["suits_details"] = suite_dict
        suite_report["report_product"] = "GEMPYP"       
        return json.dumps(suite_report, cls=dateTimeEncoder)

    def getTestcaseCounts(self):
        """
        return the no. of testcases
        """
        group = self.testcase_details.groupby(["status"]).size()
        group = group.to_dict()
        total = 0
        for i in group:
            total += group[i]
        group["total"] = total

        return group

    def validateSrunidInDB(self,jewel_user,s_run_id,username,bridgetoken):
        if jewel_user:
            # if "RUN_ID" in params:
            if s_run_id:
                logging.info("************Trying to check If s_run_id is present in DB*****************")
                # response =  dataUpload.checkingData(s_run_id, params["BRIDGE_TOKEN"], params["USERNAME"])
                if DefaultSettings.apiSuccess:
                    if not dataUpload.checkingData(s_run_id,bridgetoken, username):
                        logging.info("************s_run_id not present in DB Trying to call Post*****************")
                        dataUpload.sendSuiteData((self.toSuiteJson()), bridgetoken,username)
                    else:
                        logging.info("---------s_run_id already present --------------")
                        dataUpload.sendSuiteData((self.toSuiteJson()), bridgetoken, username,mode="PUT")
            else:
                if DefaultSettings.apiSuccess:
                    dataUpload.sendSuiteData((self.toSuiteJson()), bridgetoken, username)
                    ### first try to rerun the data
                    self.retryUploadSuiteData(bridgetoken,username)

    
    def retryUploadSuiteData(self,bridgetoken,username):
            # if dataUpload.suite_uploaded == False:
            if not dataUpload.suite_uploaded:
                        logging.info("------Retrying to Upload Suite Data------")
                        dataUpload.sendSuiteData((self.toSuiteJson()), bridgetoken, username)


    def retryUploadTestcases(self,s_run_id,bridgetoken,username,output_folder):
        jewel = ''
        unuploaded_path = ""
        failed_Utestcases=0
        # if dataUpload.suite_uploaded == True:
        if dataUpload.suite_uploaded:
            jewelLink = DefaultSettings.getUrls('jewel-url')
            jewel = f'{jewelLink}/#/autolytics/execution-report?s_run_id={s_run_id}&p_id={DefaultSettings.project_id}'
        if len(dataUpload.not_uploaded) != 0 and dataUpload.suite_uploaded:
            logging.info("------Trying again to Upload Testcase------")
            for testcase in dataUpload.not_uploaded:
                dataUpload.sendTestcaseData(testcase,bridgetoken, username)
            # if dataUpload.flag:
                # logging.warning("Testcase may be present with same tc_run_id in database")
            # unuploaded_path=self.unuploadedFile(output_folder,dataUpload.not_uploaded,"Unploaded_testCases.json")
            # failed_Utestcases = len(dataUpload.not_uploaded) 
            ### Creating file for unuploaded testcases
            # if len(dataUpload.not_uploaded) != 0:
            #     if dataUpload.flag == True:
            #         logging.warning("Testcase may be present with same tc_run_id in database")
            #     unuploaded_path=self.unuploadedFile(output_folder,dataUpload.not_uploaded,"Unploaded_testCases.json")
        # return jewel,failed_Utestcases,unuploaded_path
        return jewel,failed_Utestcases


    def WriteSuiteFile(self,base_url,output_folder,username,bridge_token):
            if not base_url:
                logging.warning("Maybe username or bridgetoken is missing or wrong thus data is not uploaded in db.")
            dataUpload.suite_data.append(self.toSuiteJson())
            unuploaded_dict = {}
            unuploaded_dict["suite_data"] = dataUpload.suite_data
            unuploaded_dict["testcases"] = dataUpload.not_uploaded
            # unuploaded_dict["urls"] = DefaultSettings.urls['data']
            unuploaded_dict["base_url"] = checkUrl(base_url)
            unuploaded_dict["user_name"] = username
            unuploaded_dict["bridge_token"] = bridge_token
            unuploaded_path=self.unuploadedFile(output_folder,unuploaded_dict,"Unuploaded_data.json")
            return unuploaded_path


    ### Function to create unuploadedFile
    def unuploadedFile(self,output_folder,data,fileName):
        unuploaded_path = ""
        # listToStr = ',\n'.join(map(str, data))
        unuploaded_path = os.path.join(output_folder, fileName)
        data = str(data)
        fernet = Fernet(encrypt_key)
        data = fernet.encrypt(data.encode())
        with open(unuploaded_path,'wb') as w:
            w.write(data)
        return unuploaded_path
        


   
