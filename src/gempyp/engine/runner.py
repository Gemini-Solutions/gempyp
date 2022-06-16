import logging
import inspect
import sys
import os
import traceback
import uuid
from typing import Dict, List, Tuple
import importlib
from gempyp.libs import common
from gempyp.engine.gempypHelper import Gempyp
from gempyp.libs.common import moduleImports


def testcaseRunner(testcaseMeta: Dict) -> Tuple[List, Dict]:
    """
    actually imports the testcase functions and run the functions
    """
    print("------------------ In testcase Runner --------------")
    configData: Dict = testcaseMeta.get("configData")
    logger = configData.get("logger")
    testcaseMeta.pop("configData")
    try:
        fileName = configData.get("PATH")

        dynamicTestcase = moduleImports(fileName)
        print("-----------------------------------------------------------")

        try:
            # TODO update the confidData to contain some default values
            # GEMPYPFOLDER
            allClasses = inspect.getmembers(dynamicTestcase, inspect.isclass)
            # print("!!!!!!!!!!! allclasses \n", allClasses, "\n!!!!!!!!!!!!!!")

            for name, cls in allClasses:
                # currently running only one class easily extensible to run multiple classes
                # from single file
                if (
                    issubclass(cls, Gempyp)
                    and name != "Gempyp"
                ):

                    print("------- In subclass check --------")
                    ResultData = cls().RUN(cls, configData, **testcaseMeta)

                    break
            # testcase has successfully ran
            # make the output Dictt
            output = []
            for data in ResultData:
                tempdict = {}
                # TODO
                # MAKE the TC_RUNID
                unique_id = uuid.uuid4()
                try:
                    if os.environ.get('unique_id'):
                        unique_id = os.environ.get('unique_id')
                except Exception:
                    traceback.print_exc()
                tc_run_id = f"{data['NAME']}_{unique_id}"
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
                data["jsonData"]["metaData"][2]["TOTAL"] = total

                # have to look into the way on how to get the log file
                try:
                    log_file = os.path.join(os.environ.get('log_dir'),data['NAME']+'_'+unique_id+'.log')
                except Exception:
                    log_file = None
                tempdict["log_file"] = log_file 

                singleTestcase = {}
                singleTestcase["testcaseDict"] = tempdict
                singleTestcase["misc"] = data.get("MISC")
                singleTestcase["jsonData"] = data.get("jsonData")
                output.append(singleTestcase)
            return output, None

        except Exception as e:
            logger.error("Error occured while running the testcase: {e}".format(e=e))
            return None, getError(e, configData)
 
    except Exception as e:
        logger.error("Some Error occured while making the testcase: {e}".format(e=e))
        return None, getError(e, configData)


def getError(error, configData: Dict) -> Dict:

    error = {}
    error["testcase"] = configData.get("NAME")
    error["message"] = str(error)
    error["product_type"] = "GEMPYP"
    error["category"] = configData.get("CATEGORY", None)
    error['log_path'] = configData.get('log_path', None)

    return error
