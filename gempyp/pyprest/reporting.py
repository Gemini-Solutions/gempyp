from asyncio.log import logger
import traceback
import os
import uuid
import time
import json
import logging


def writeToReport(pyprest_obj):
    """
    This function takes pyprest obj,
    creates the testcase report if the runmode is debug mode,
    Creates the dictionary that is to be sent to gempyp"""
    result = {}
    if not pyprest_obj.reporter.result_file_name:
        try:
            try:
                pyprest_obj.reporter.finalizeReport()   ## need to test
                if pyprest_obj.data.get("OUTPUT_FOLDER", pyprest_obj.default_report_path) is None:
                    os.makedirs(pyprest_obj.data.get("OUTPUT_FOLDER", pyprest_obj.default_report_path))
            except Exception as e:
                pyprest_obj.logger.info(traceback.print_exc())
            pyprest_obj.reporter.json_data = pyprest_obj.reporter.template_data.makeTestcaseReport()
            pyprest_obj.json_data = pyprest_obj.reporter.json_data
            result = pyprest_obj.reporter.serialize()
            if pyprest_obj.data["config_data"].get("DEBUG_MODE", "FALSE").upper() == "TRUE":
                # make report
                try:
                    makeReport_pypRest(pyprest_obj, json.dumps(pyprest_obj.reporter.json_data))
                    pyprest_obj.logger.info("-------file_dumped---------")
                except Exception as e:
                    pyprest_obj.logger.info(str(e))

        except Exception as e:
            pyprest_obj.logger.info(traceback.print_exc())
    output = []
    tempdict = {} 
    tc_run_id = f"{pyprest_obj.tcname}_{uuid.uuid4()}"
    tempdict["tc_run_id"] = tc_run_id
    print("tc_run_id=",tc_run_id)
    tempdict["name"] = result["NAME"]
    tempdict["category"] = pyprest_obj.category
    tempdict["status"] = result["STATUS"]
    tempdict["user"] = pyprest_obj.data.get("USER")
    tempdict["machine"] = pyprest_obj.data.get("MACHINE")
    tempdict["product type"] = "GEMPYP-PR"
    tempdict["result_file"] = result["RESULT_FILE"]
    tempdict["start_time"] = result["START_TIME"]
    tempdict["end_time"] = result["END_TIME"]
    tempdict["ignore"] = False
    all_status = result["json_data"]["metaData"][2]
    total = 0
    for key in all_status:
        total += all_status[key]
    result["json_data"]["metaData"][2]["TOTAL"] = total
    unsorted_dict = result["json_data"]["metaData"][2]
    sorted_dict = dict( sorted(unsorted_dict.items(), key=lambda x: x[0].lower(), reverse=True) )
    result["json_data"]["metaData"][2] = sorted_dict

    # getting the log file ( the custom gempyp logger)
    
    tempdict["log_file"] = pyprest_obj.data.get("LOG_PATH", "N.A")

    singleTestcase = {}
    singleTestcase["testcase_dict"] = tempdict
    singleTestcase["misc"] = result.get("MISC")
    singleTestcase["json_data"] = pyprest_obj.json_data
    singleTestcase["suite_variables"] = pyprest_obj.variables["suite"]
    output.append(singleTestcase)
    return output


def makeReport_pypRest(obj, json_data):
        # Create testcase file in the given output folder when in debug mode

        index_path = os.path.dirname(__file__)
        result_data = ""
        index_path = os.path.join(os.path.split(index_path)[0], "testcase.html")
        with open(index_path, "r") as f:
            result_data = f.read()

        result_data = result_data.replace("::DATA::", json_data)

        result_file = os.path.join(obj.data.get("OUTPUT_FOLDER"), f"{obj.reporter.testcase_name + str(time.time())}.html")
        with open(result_file, "w+") as f:
            f.write(result_data)