import traceback
import os
import uuid
import time


def write_to_report(pyprest_obj):
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
            # make report
            # pyprest_obj.makeReport(json.dumps(pyprest_obj.reporter.jsonData))
            # print("-------file_dumped---------")

        except Exception as e:
            traceback.print_exc()
    output = []
    tempdict = {} 
    tc_run_id = f"{pyprest_obj.data['NAME']}_{uuid.uuid4()}"
    tempdict["tc_run_id"] = tc_run_id
    tempdict["name"] = result["NAME"]
    tempdict["category"] = pyprest_obj.data.get("CATEGORY")
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