import pandas as pd
import traceback
import json
from gempyp.libs.common import dateTimeEncoder


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
        ]
        self.misc_detail_column = ["run_id", "key", "value", "table_type"]

        # can have anyamount of columns
        # this should always have one row so it can be made a dict or something instad of a dataframe
        self.suite_detail = pd.DataFrame()

        self.testcase_details = pd.DataFrame(columns=self.testcase_detail_column)
        self.misc_details = pd.DataFrame(columns=self.misc_detail_column)

    def toSuiteJson(self):
        """
        converts the dataframe to Json
        used in uploadsuitedata (run() method in engine.py)
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
        returns the json for testcasedata
        used in update_df method of engine.py
        """

        test_data = self.testcase_details.loc[
            self.testcase_details["tc_run_id"].str.upper() == tc_run_id
        ]
        if test_data.empty:
            return {}
        test_data = test_data.to_dict(orient="records")[0]
        misc_data = self.misc_details.loc[self.misc_details["run_id"].str.upper() == tc_run_id]
        misc_data = misc_data.to_dict(orient="records")

        test_data["misc_data"] = misc_data
        test_data["s_run_id"] = s_run_id
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
