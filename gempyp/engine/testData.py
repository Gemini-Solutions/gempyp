from cmath import nan
import logging
import pandas as pd
import traceback
import json
from gempyp.libs.common import dateTimeEncoder, findDuration
from datetime import datetime, timezone
import numpy as np


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
            "user",
            "machine",
            "result_file",
            "product_type",
            "ignore",
            "miscData",
            "userDefinedData",
            "duration"
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

        misc_data = misc_data.to_dict(orient="records")
        data["misc_data"] = misc_data
        data["s_id"] = "test_id"
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
        test_data["duration"] = findDuration(test_data["start_time"], test_data["end_time"])

        test_data["userDefinedData"] = dict()
        # test_data["response_time"]="{0:.{1}f} sec(s)".format((test_data["end_time"]-test_data["start_time"]).total_seconds(),2)
        """ Adding misc data to userDefinedData column for each testcase
        Here misc data is only for one testcase.
        {"key1": "value1", "key2": "value2"...}"""
        if len(misc_data) > 0:
            for miscs in misc_data:
                print("--- misc key", miscs.get("key", None))
                key = str(miscs["key"])
                val = str(miscs["value"])
                test_data["userDefinedData"][key] = val

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

        test_data["miscData"] = meta_data
        test_data["s_run_id"] = s_run_id
        test_data["userDefinedData"]["response_time"]="{0:.{1}f} sec(s)".format((test_data["end_time"]-test_data["start_time"]).total_seconds(),2)
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
        misc_dict=self.misc_details.to_dict(orient="records")
        try:

            # converting testcase_dict to dict for easy parsing
            test_dict = {d['tc_run_id']: d for d in testcase_dict}
            key = list(test_dict.keys())
            key = key[0]
            test_data = test_dict[key]
            test_data.pop("userDefinedData")
            test_data.pop("miscData")
            test_dict[key] = test_data
            for each_misc in misc_dict:
                test_dict[each_misc['run_id']][each_misc["key"]] = each_misc["value"]

            # converting dict back to list
            testcase_dict = [test_dict[tc_run_id] for tc_run_id in test_dict.keys()]
        except Exception as e:
            traceback.print_exc()

        # testcase_dict.remove("userDefinedData")
        # testcase_dict.remove("miscData")
        for i in range(len(testcase_dict)):
            if("miscData" in testcase_dict[i].keys()):
                testcase_dict[i].pop("miscData")
            if("userDefinedData" in testcase_dict[i].keys()):
                testcase_dict[i].pop("userDefinedData")
        suite_dict["TestCase_Details"] = testcase_dict
        testcase_counts = self.getTestcaseCounts()
        prio_list = ['total', 'PASS', 'FAIL']
        sorted_dict = {}
        for key in prio_list:
            if key in testcase_counts :
                sorted_dict[key] = testcase_counts[key]
                testcase_counts.pop(key)
            elif key == "PASS" or key == 'FAIL':
                sorted_dict[key] = 0
        sorted_dict.update(testcase_counts)
        testcase_counts = sorted_dict
        suite_dict["Testcase_Info"] = testcase_counts
        suite_report["Suits_Details"] = suite_dict
        suite_report["reportProduct"] = "GEMPYP"       
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
