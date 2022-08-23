import pandas as pd
import traceback
import json
from gempyp.libs.common import dateTimeEncoder, findDuration
from datetime import datetime, timezone


class TestData:
    def __init__(self):
        self.testcase_detail_column = [
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
        ]
        self.misc_detail_column = ["run_id", "key", "value", "table_type"]

        # can have anyamount of columns
        # this should always have one row so it can be made a dict or something instad of a dataframe
        self.suite_detail = pd.DataFrame()

        self.testcase_details = pd.DataFrame(columns=self.testcase_detail_column)
        self.misc_details = pd.DataFrame(columns=self.misc_detail_column)

    def toSuiteJson(self):
        """
        converts the dataframe to suiteJson
        """
        if self.suite_detail.empty:
            return {}

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
        returns the testcase for that specific json
        """

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
                test_status.get(key) + 1
            else:
                test_status[key] = 1
        test_status["TOTAL"] = sum(test_status.values())

        test_data["userDefinedData"] = dict()
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
                "DATE OF EXECUTION": {"value": datetime.now(timezone.utc), "type": "date"}
            }, 
            {
                "EXECUTION STARTED ON": {"value": test_data["start_time"], "type": "datetime"},
                "EXECUTION ENDED ON": {"value": test_data["end_time"], "type": "datetime"}, 
                "EXECUTION DURATION": findDuration(test_data["start_time"], test_data["end_time"])
            }, 
            test_status]


        test_data["miscData"] = meta_data
        test_data["s_run_id"] = s_run_id
        return json.dumps(test_data, cls=dateTimeEncoder)

    def _validate(self):
        """
        used by fromJSON to validate the json data
        """
        pass

    def getJSONData(self):
        """
        provide the report json
        """
        suite_report = {}
        suite_dict = self.suite_detail.to_dict(orient="records")[0]
        testcase_dict = self.testcase_details.to_dict(orient="records")
        misc_dict=self.misc_details.to_dict(orient="records")
        try:

            # converting testcase_dict to dict for easy parsing
            test_dict = {d['tc_run_id']: d for d in testcase_dict}
            for each_misc in misc_dict:
                test_dict[each_misc['run_id']][each_misc["key"]] = each_misc["value"]

            # converting dict back to list
            testcase_dict = [test_dict[tc_run_id] for tc_run_id in test_dict.keys()]
        except Exception as e:
            traceback.print_exc()


        suite_dict["TestCase_Details"] = testcase_dict
        testcase_counts = self.getTestcaseCounts()
        suite_dict["Testcase_Info"] = testcase_counts
        suite_report["Suite_Details"] = suite_dict
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
