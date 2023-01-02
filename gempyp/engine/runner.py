import logging
import inspect
import os
import traceback
import uuid
from typing import Dict, List, Tuple
from gempyp.engine.simpleTestcase import AbstractSimpleTestcase
from gempyp.libs.common import moduleImports
import getpass
from gempyp.libs.common import download_beforeAfter_file


def testcaseRunner(testcase_meta: Dict) -> Tuple[List, Dict]:

    """
    actually imports the testcase files and call the run method 
    set the json data that is required to update in db
    """
    logging.info("---------- In testcase Runner -----------")
    config_data: Dict = testcase_meta.get("config_data")
    logger = config_data.get("LOGGER")
    testcase_meta.pop("config_data")
    try:
        file_name = config_data.get("PATH")
        dynamic_testcase =download_beforeAfter_file(file_name,testcase_meta.get("SUITE_VARS",None))
        try:
            # TODO update the config_data to contain some default values
            # GEMPYPFOLDER
            all_classes = inspect.getmembers(dynamic_testcase, inspect.isclass)

            for name, cls in all_classes:
                # currently running only one class easily extensible to run multiple classes
                # from single file
                if (
                    issubclass(cls, AbstractSimpleTestcase)
                    and name != "AbstractSimpleTestcase"
                ):

                    print("------- In subclass check --------")
                    result_data = cls().RUN(cls, config_data, **testcase_meta)


                    break
            # testcase has successfully ran
            # make the output Dict
            output = []

            for data in result_data:
                data["TESTCASEMETADATA"] = testcase_meta
                data["config_data"] = config_data

                singleTestcase = getOutput(data)

                output.append(singleTestcase)
            return output, None

        except Exception as e:
            logger.error("Error occured while running the testcase: {e}".format(e=e))
            return None, getError(e, config_data)
 
    except Exception as e:
        logger.error("Some Error occured while making the testcase: {e}".format(e=e))
        return None, getError(e, config_data)

def getOutput(data):
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
    tempdict["category"] = data["config_data"].get("CATEGORY", None)
    tempdict["status"] = data["STATUS"]
    tempdict["base_user"] = getpass.getuser()
    tempdict["invoke_user"] = data["TESTCASEMETADATA"]["INVOKE_USER"]
    tempdict["machine"] = data["TESTCASEMETADATA"]["MACHINE"]
    tempdict["product_type"] = "GEMPYP"
    tempdict["result_file"] = data["RESULT_FILE"]
    tempdict["start_time"] = data["START_TIME"]
    tempdict["end_time"] = data["END_TIME"]
    tempdict["ignore"] = True if data["TESTCASEMETADATA"].get("IGNORE") else False
    # tempdict["response_time"]="{0:.{1}f} sec(s)".format((data["END_TIME"]-data["START_TIME"]).total_seconds(),2)

    all_status = data["json_data"]["meta_data"][2]
    total = 0
    for key in all_status:
        total = total + all_status[key]
    data["json_data"]["meta_data"][2]["TOTAL"] = total
    try:
        log_file= os.path.join('logs',data['NAME']+'_'+unique_id+'.log')
    except Exception:
        log_file = None
    tempdict["log_file"] = log_file 

    singleTestcase = {}
    singleTestcase["testcase_dict"] = tempdict
    singleTestcase["misc"] = data.get("MISC")
    singleTestcase["json_data"] = data.get("json_data")
    return singleTestcase

def getError(error, config_data: Dict) -> Dict:
    """
    returning the dictionary of error teatCase data
    """
    error = {}
    error["testcase"] = config_data.get("NAME")
    error["message"] = str(error)
    error["product_type"] = "GEMPYP"
    error["category"] = config_data.get("CATEGORY", None)
    error['log_path'] = config_data.get('log_path', None)
    return error
