import inspect
import uuid
from typing import Dict, List, Tuple
import logging
import importlib
from gempyp.libs import common
from gempyp.engine.simpleTestcase import AbstarctSimpleTestcase


def testcaseRunner(testcaseMeta: Dict) -> Tuple[List, Dict]:
    """
    actually imports the testcase functions and run the functions
    """
    configData: Dict = testcaseMeta.get("configData")
    testcaseMeta.pop("configData")
    try:
        fileName = configData.get("PATH")

        try:
            dynamicTestcase = importlib.import_module(fileName)
        except ImportError as i:
            common.errorHandler(logging, i, "testcase file could not be imported")
            return None, getError(i, configData)

        try:
            # TODO update the confidData to contain some default values
            # GEMPYPFOLDER
            allClasses = inspect.getmembers(dynamicTestcase, inspect.isclass)

            for name, cls in allClasses:
                # currently running only one class easily extensible to run multiple classes
                # from single file
                if (
                    issubclass(cls, AbstarctSimpleTestcase)
                    and name != "AbstarctSimpleTestcase"
                ):
                    ResultData = cls().RUN(configData, **testcaseMeta)
                    break

            # testcase has successfully ran
            # make the output Dictt
            output = []
            for data in ResultData:
                tempdict = {}
                # TODO
                # MAKE the TC_RUNID
                tc_run_id = f"{data['NAME']}_{uuid.uuid4()}"
                tempdict["tc_run_id"] = tc_run_id
                tempdict["name"] = data["NAME"]
                tempdict["category"] = configData.get("CATEGORY")
                tempdict["status"] = data["STATUS"]
                tempdict["user"] = testcaseMeta["USER"]
                tempdict["machine"] = testcaseMeta["MACHINE"]
                tempdict["product_type"] = "GEMPYP"
                tempdict["result_file"] = data["RESULT_FILE"]
                tempdict["start_time"] = data["START_TIME"]
                tempdict["end_time"] = data["END_TIME"]
                tempdict["ignore"] = True if testcaseMeta.get("IGNORE") else False

                all_status = data["jsonData"]["metaData"][2]
                total = 0
                for key in all_status:
                    total = total + all_status[key]
                # print("-------------- total", total)
                data["jsonData"]["metaData"][2]["TOTAL"] = total

                # have to look into the way on how to get the log file
                tempdict["log_file"] = None

                singleTestcase = {}
                singleTestcase["testcaseDict"] = tempdict
                singleTestcase["misc"] = data.get("MISC")
                singleTestcase["jsonData"] = data.get("jsonData")
                # print("-------------- singleTestcase\n ", tempdict, "\n--------")
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
    error["testcase"] = configData.get("NAME")
    error["message"] = str(error)
    error["product_type"] = "GEMPYP"
    error["category"] = configData.get("CATEGORY", None)

    return error
