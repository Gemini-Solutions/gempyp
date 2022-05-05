import pandas as pd
import json
from gempyp.libs.common import dateTimeEncoder


class testData:
    def __init__(self):
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
        self.miscDetailColumn = ["run_id", "key", "value", "table_type"]

        # can have anyamount of columns
        # this should always have one row so it can be made a dict or something instad of a dataframe
        self.suiteDetail = pd.DataFrame()

        self.testcaseDetails = pd.DataFrame(columns=self.testcaseDetailColumn)
        self.miscDetails = pd.DataFrame(columns=self.miscDetailColumn)

    def toSuiteJson(self):
        """
        converts the dataframe to suiteJson
        """
        if self.suiteDetail.empty:
            return {}

        data = self.suiteDetail.to_dict(orient="records")[0]
        # print("-------- data for suite \n", data, "\n---------")
        miscData = self.miscDetails[
            self.miscDetails["table_type"].str.upper() == "SUITE"
        ]

        miscData = miscData.to_dict(orient="records")
        data["miscData"] = miscData
        data["s_id"] = "test_id"
        # data["testcaseDetails"] = self.testcaseDetails.to_dict(orient="records")

        return json.dumps(data, cls=dateTimeEncoder)

    def totestcaseJson(self, tc_run_id, s_run_id):
        """
        returns the testcase for that specific json
        """

        testData = self.testcaseDetails.loc[
            self.testcaseDetails["tc_run_id"].str.upper() == tc_run_id
        ]
        if testData.empty:
            return {}
        testData = testData.to_dict(orient="records")[0]
        miscData = self.miscDetails.loc[self.miscDetails["run_id"].str.upper() == tc_run_id]
        miscData = miscData.to_dict(orient="records")

        testData["miscData"] = miscData
        testData["s_run_id"] = s_run_id
        # print("-----------\n testData", testData, "\n------------")
        return json.dumps(testData, cls=dateTimeEncoder)

    def _validate(self):
        """
        used by fromJSON to validate the json data
        """
        pass

    def getJSONData(self):
        """
        provide the report json
        """
        SuiteReport = {}
        suiteDict = self.suiteDetail.to_dict(orient="records")[0]
        testcaseDict = self.testcaseDetails.to_dict(orient="records")
        suiteDict["TestCase_Details"] = testcaseDict
        print("------\n testcaseDict", testcaseDict, "\n --------------")
        testcase_counts = self.getTestcaseCounts()
        suiteDict["Testcase_Info"] = testcase_counts
        SuiteReport["Suits_Details"] = suiteDict
        SuiteReport["reportProduct"] = "GEMPYP"        

        return json.dumps(SuiteReport, cls=dateTimeEncoder)

    def getTestcaseCounts(self):

        group = self.testcaseDetails.groupby(["status"]).size()
        group = group.to_dict()
        total = 0
        for i in group:
            total += group[i]
        group["total"] = total

        return group
