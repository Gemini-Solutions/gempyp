import logging
import inspect
import os
import traceback
import uuid
from typing import Dict, List, Tuple
from gempyp.engine.simpleTestcase import AbstractSimpleTestcase
import getpass
from gempyp.libs.common import download_common_file, moduleImports
from gempyp.libs.gem_s3_common import uploadToS3, create_s3_link
from gempyp.config import DefaultSettings
import re

def testcaseRunner(testcase_meta: Dict) -> Tuple[List, Dict]:
    result_data = None
    """
    actually imports the testcase files and call the run method 
    set the json data that is required to update in db
    """
    logging.info("---------- In testcase Runner -----------")
    config_data: Dict = testcase_meta.get("config_data")
    if testcase_meta.get("default_urls", None):
        DefaultSettings.urls.update(testcase_meta.get("default_urls"))  # only for optimized mode, urls not shared between processes
    logger = config_data.get("LOGGER")
    testcase_meta.pop("config_data")
    try:
        file_name = config_data.get("PATH")
        file_path = download_common_file(file_name,testcase_meta.get("SUITE_VARS",None))
        dynamic_testcase = moduleImports(file_path)
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

                    logging.info("------- In subclass check --------")
                    result_data = cls().RUN(cls, config_data, **testcase_meta)


                    break
            # testcase has successfully ran
            # make the output Dict
            output = []
            if result_data:
                for data in result_data:
                    data["TESTCASEMETADATA"] = testcase_meta
                    data["config_data"] = config_data

                    singleTestcase = getOutput(data)

                    output.append(singleTestcase)
                return output, None
            raise Exception("Testcase not found")
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
    tc_run_id=re.sub(r'[^a-zA-Z0-9]', '_',tc_run_id)
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
        log_file= os.path.join('logs',data['NAME']+'_'+unique_id+'.txt')  # ## replacing log with txt for UI compatibility
    except Exception:
        log_file = None
    tempdict["log_file"] = log_file
    try:
        # s3_log_file_url= create_s3_link(url=uploadToS3(DefaultSettings.urls["data"].get("s3preSigned","https://betaapi.gemecosystem.com/gemEcosystemS3/s3/v1/generatePreSigned"), bridge_token=data.get("TESTCASEMETADATA").get("SUITE_VARS", None).get("bridge_token",None), username=data.get("TESTCASEMETADATA").get("SUITE_VARS", None).get("username",None), file=data["config_data"].get("log_path", data["config_data"].get("LOG_PATH", "N.A")),tag="public")[0]["Url"])
        s3_log_file_url= uploadToS3(DefaultSettings.urls["data"].get("pre-signed",None), bridge_token=data.get("TESTCASEMETADATA").get("SUITE_VARS", None).get("bridge_token",None), username=data.get("TESTCASEMETADATA").get("SUITE_VARS", None).get("username",None), file=data["config_data"].get("log_path", data["config_data"].get("LOG_PATH", "N.A")),tag="protected",s_run_id=data["TESTCASEMETADATA"].get("S_RUN_ID"))[0]
        # s3_log_file_url = f'<a href="{s3_log_file_url}" target=_blank>view</a>'
    except Exception:
        s3_log_file_url = None
    singleTestcase = {}
    singleTestcase["testcase_dict"] = tempdict
    singleTestcase["misc"] = data.get("MISC")
    singleTestcase["json_data"] = data.get("json_data")
    singleTestcase["misc"]["log_file"] = s3_log_file_url
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
