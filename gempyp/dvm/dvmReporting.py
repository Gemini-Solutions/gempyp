import traceback
import os
import uuid
import time
import json
import logging


def writeToReport(dvm_obj):
    """
    This function takes DVM obj,
    creates the testcase report if the runmode is debug mode,
    Creates the dictionary that is to be sent to gempyp"""
    result = {}
    if not dvm_obj.reporter.result_file_name:
        try:
            try:
                dvm_obj.reporter.finalizeReport()   ## need to test
                if dvm_obj.data.get("OUTPUT_FOLDER", dvm_obj.default_report_path) is None:
                    os.makedirs(dvm_obj.data.get("OUTPUT_FOLDER", dvm_obj.default_report_path))
            except Exception as e:
                dvm_obj.logger.info(traceback.print_exc())
            dvm_obj.reporter.json_data = dvm_obj.reporter.template_data.makeTestcaseReport()
            dvm_obj.json_data = dvm_obj.reporter.json_data
            result = dvm_obj.reporter.serialize()
        except Exception as e:
            # dvm_obj.logger.info(traceback.print_exc())
            traceback.print_exc()
    result = dvm_obj.reporter.serialize()
    output = []
    tempdict = {} 
    tc_run_id = f"{dvm_obj.tcname}_{uuid.uuid4()}"
    tempdict["tc_run_id"] = tc_run_id
    tempdict["name"] = result["NAME"]
    tempdict["category"] = dvm_obj.category
    tempdict["status"] = result["STATUS"]
    tempdict["user"] = dvm_obj.data.get("USER")
    tempdict["machine"] = dvm_obj.data.get("MACHINE")
    tempdict["product type"] = "GEMPYP-DV"
    tempdict["steps"] = result["json_data"]['steps']
    tempdict["result_file"] = result["RESULT_FILE"]
    tempdict["start_time"] = result["START_TIME"]
    tempdict["end_time"] = result["END_TIME"]
    tempdict["ignore"] = False
    all_status = result["json_data"]["metaData"][2]
    total = 0
    for key in all_status:
        total += all_status[key]
    result["json_data"]["metaData"][2]["TOTAL"] = total

    # getting the log file ( the custom gempyp logger)
    
    tempdict["log_file"] = dvm_obj.configData.get("log_path","N.A")

    singleTestcase = {}
    singleTestcase["testcase_dict"] = tempdict
    singleTestcase["misc"] = result.get("MISC")
    singleTestcase["json_data"] = dvm_obj.json_data
    output.append(singleTestcase)
    
    return output