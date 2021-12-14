import pandas as pd

class testData():
    
    def __init__(self):
        self.suiteColumns = ["s_run_id", "s_start_time", "s_end_time", "status", "projectName", "run_type", "s_report_type"]
        self.multiRunColumns = ["s_run_id", "r_run_id", "r_start_time","r_end_time" "user", "status", "run_type", "env", "machine", "initiated_by", "run_mode"]
        self.testcaseDetailColumn = ["tc_run_id", "s_run_id", "r_run_id", "tc_start_time", "tc_end_time",  "status", "user", "machine", "result_file", "ignore"]
        self.miscDetailColumn = ["run_id", "key" ,"value"]

        self.suiteDetail = pd.DataFrame(columns=self.suiteColumns)
        self.multiRunColumns = pd.DataFrame(columns=self.multiRunColumns)
        self.testcaseDetailColumn = pd.DataFrame(columns=self.testcaseDetailColumn)
        self.miscDetailColumn = pd.DataFrame(columns=self.miscDetailColumn)

    
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



    



