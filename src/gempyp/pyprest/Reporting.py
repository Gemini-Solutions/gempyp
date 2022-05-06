import traceback
import os
import uuid
import time


def write_to_report(pirest_obj):
    result = {}
    if not pirest_obj.reporter.resultFileName:
        try:
            try:
                os.makedirs(pirest_obj.data.get("OUTPUT_FOLDER", pirest_obj.default_report_path))
            except Exception as e:
                traceback.print_exc()
            pirest_obj.reporter.jsonData = pirest_obj.reporter.templateData.makeReport(
                pirest_obj.data.get("OUTPUT_FOLDER"), pirest_obj.reporter.testcaseName + str(time.time()))
            pirest_obj.jsonData = pirest_obj.reporter.jsonData
            result = pirest_obj.reporter.serialize()
            # make report
            # pirest_obj.makeReport(json.dumps(pirest_obj.reporter.jsonData))
            # print("-------file_dumped---------")

        except Exception as e:
            traceback.print_exc()
    output = []
    tempdict = {} 
    tc_run_id = f"{pirest_obj.data['NAME']}_{uuid.uuid4()}"
    tempdict["tc_run_id"] = tc_run_id
    tempdict["name"] = result["NAME"]
    tempdict["category"] = pirest_obj.data.get("CATEGORY")
    tempdict["status"] = result["STATUS"]
    tempdict["user"] = pirest_obj.data.get("USER")
    tempdict["machine"] = pirest_obj.data.get("MACHINE")
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
    singleTestcase["jsonData"] = pirest_obj.jsonData
    output.append(singleTestcase)

    print(output)
    return output