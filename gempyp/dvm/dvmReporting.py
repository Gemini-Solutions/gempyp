import traceback
import os
import uuid
import time
import json
import logging


def writeToReport(dvm_obj):
    """
    This function takes pyprest obj,
    creates the testcase report if the runmode is debug mode,
    Creates the dictionary that is to be sent to gempyp"""
    result = {}
    if not dvm_obj.reporter.resultFileName:
        try:
            try:
                dvm_obj.reporter.finalize_report()   ## need to test
                if dvm_obj.data.get("OUTPUT_FOLDER", dvm_obj.default_report_path) is None:
                    os.makedirs(dvm_obj.data.get("OUTPUT_FOLDER", dvm_obj.default_report_path))
            except Exception as e:
                dvm_obj.logger.info(traceback.print_exc())
            dvm_obj.reporter.jsonData = dvm_obj.reporter.templateData.makeReport(
                dvm_obj.data.get("OUTPUT_FOLDER"), dvm_obj.reporter.testcaseName + str(time.time()))
            dvm_obj.jsonData = dvm_obj.reporter.jsonData
            result = dvm_obj.reporter.serialize()

        except Exception as e:
            # dvm_obj.logger.info(traceback.print_exc())
            traceback.print_exc()
    output = []
    tempdict = {} 
    tc_run_id = f"{dvm_obj.tcname}_{uuid.uuid4()}"
    tempdict["tc_run_id"] = tc_run_id
    tempdict["name"] = result["NAME"]
    tempdict["category"] = dvm_obj.category
    tempdict["status"] = result["STATUS"]
    tempdict["user"] = dvm_obj.data.get("USER")
    tempdict["machine"] = dvm_obj.data.get("MACHINE")
    tempdict["product_type"] = "DVM"
    tempdict["result_file"] = result["RESULT_FILE"]
    tempdict["start_time"] = result["START_TIME"]
    tempdict["end_time"] = result["END_TIME"]
    tempdict["ignore"] = False
    all_status = result["jsonData"]["metaData"][2]
    total = 0
    for key in all_status:
        total += all_status[key]
    result["jsonData"]["metaData"][2]["TOTAL"] = total

    # getting the log file ( the custom gempyp logger)
    
    tempdict["log_file"] = dvm_obj.data.get("LOG_PATH", "N.A")

    singleTestcase = {}
    singleTestcase["testcaseDict"] = tempdict
    singleTestcase["misc"] = result.get("MISC")
    singleTestcase["jsonData"] = dvm_obj.jsonData
    output.append(singleTestcase)
    
    return output