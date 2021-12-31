import pandas as pd


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

    def toJSON(self):
        """
        converts the whole data to json
        """
        pass

    def fromJSON(self, data):
        """
        converts the json data to the object
        """
        pass

    def _validate(self):
        """
        used by fromJSON to validate the json data
        """
        pass
