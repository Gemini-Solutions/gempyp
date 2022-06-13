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
    if not pyprest_obj.reporter.resultFileName:
        try:
            try:
                os.makedirs(pyprest_obj.data.get("OUTPUT_FOLDER", pyprest_obj.default_report_path))
            except Exception as e:
                traceback.print_exc()
            pyprest_obj.reporter.jsonData = pyprest_obj.reporter.templateData.makeReport(
                pyprest_obj.data.get("OUTPUT_FOLDER"), pyprest_obj.reporter.testcaseName + str(time.time()))
            pyprest_obj.jsonData = pyprest_obj.reporter.jsonData
            result = pyprest_obj.reporter.serialize()
            print(pyprest_obj.data["configData"].get("DEBUG_MODE", False).upper())
            if pyprest_obj.data["configData"].get("DEBUG_MODE", False).upper() == "TRUE":
                # make report
                try:
                    makeReport(pyprest_obj, json.dumps(pyprest_obj.reporter.jsonData))
                    logging.info("-------file_dumped---------")
                except Exception as e:
                    traceback.print_exc()

        except Exception as e:
            traceback.print_exc()
    output = []
    tempdict = {} 
    tc_run_id = f"{pyprest_obj.tcname}_{uuid.uuid4()}"
    tempdict["tc_run_id"] = tc_run_id
    tempdict["name"] = result["NAME"]
    tempdict["category"] = pyprest_obj.category
    tempdict["status"] = result["STATUS"]
    tempdict["user"] = pyprest_obj.data.get("USER")
    tempdict["machine"] = pyprest_obj.data.get("MACHINE")
    tempdict["product_type"] = "gempyp"
    tempdict["result_file"] = result["RESULT_FILE"]
    tempdict["start_time"] = result["START_TIME"]
    tempdict["end_time"] = result["END_TIME"]
    tempdict["ignore"] = False
    all_status = result["jsonData"]["metaData"][2]
    total = 0
    for key in all_status:
        total = all_status[key]
    result["jsonData"]["metaData"][2]["TOTAL"] = total

    # have to look into the way on how to get the log file
    tempdict["log_file"] = None

    singleTestcase = {}
    singleTestcase["testcaseDict"] = tempdict
    singleTestcase["misc"] = result.get("MISC")
    singleTestcase["jsonData"] = pyprest_obj.jsonData
    output.append(singleTestcase)

    return output


def makeReport(obj, jsonData):
        # Create testcase file in the given output folder when in debug mode

        index_path = os.path.dirname(__file__)
        Result_data = ""
        index_path = os.path.join(os.path.split(index_path)[0], "testcase.html")
        with open(index_path, "r") as f:
            Result_data = f.read()

        Result_data = Result_data.replace("::DATA::", jsonData)

        result_file = os.path.join(obj.data.get("OUTPUT_FOLDER"), f"{obj.reporter.testcaseName + str(time.time())}.html")
        with open(result_file, "w+") as f:
            f.write(Result_data)