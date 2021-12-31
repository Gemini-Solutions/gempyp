from typing import Dict, List, Tuple
import logging
import importlib
from pygem.libs import common


def testcaseRunner(self, testcaseMeta: Dict) -> Tuple(List, Dict):
    """ "
    actually imports the testcase functions and run the functions
    """
    configData: Dict = testcaseMeta.get("configData")
    try:
        fileName = configData.get("path")

        try:
            dynamicTestcase = importlib.import_module(fileName)
        except ImportError as i:
            common.errorHandler(logging, i, "testcase file could not be imported")
            return None, getError(i, configData)

        try:
            # TODO update the confidData to contain some default values
            # PYGEMFOLDER
            configData["PYGEMFOLDER"] = testcaseMeta["default_folder"]
            ResultData = dynamicTestcase.RUN(configData)

            # testcase has successfully ran
            # make the output Dictt
            output = []
            for data in ResultData:
                tempdict = {}
                tempdict["name"] = data["testcase_name"]
                tempdict["category"] = configData.get("category")
                tempdict["status"] = data["status"]
                tempdict["user"] = testcaseMeta["user"]
                tempdict["machine"] = testcaseMeta["machine"]
                tempdict["product_type"] = "PYGEM"
                tempdict["result_file"] = data["result_file"]
                tempdict["start_time"] = data["start_time"]
                tempdict["end_time"] = data["end_time"]

                # have to look into the way on how to get the log file
                tempdict["log_file"] = None

                singleTestcase = {}
                singleTestcase["testcaseDict"] = tempdict
                singleTestcase["misc"] = data.get("misc_data")
                output.append(singleTestcase)

            return output, None

        except Exception as e:
            common.errorHandler(logging, e, "Error occured while running the testcas")
            return None, getError(e, configData)

    except Exception as e:
        common.errorHandler(logging, e, "Some Error occured while making the testcase")

        return None, getError(e, configData)


def getError(error, configData: Dict) -> Dict:

    error = {}
    error["testcase"] = configData.get("testcase")
    error["message"] = str(error)
    error["product_type"] = "PYGEM"
    error["category"] = configData.get("category", None)

    return error
