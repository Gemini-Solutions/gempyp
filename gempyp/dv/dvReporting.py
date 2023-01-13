import traceback
import os
import uuid
import getpass
from gempyp.libs.gem_s3_common import upload_to_s3, create_s3_link
from gempyp.config import DefaultSettings


def writeToReport(dv_obj):
    """
    This function takes DVM obj,
    creates the testcase report if the runmode is debug mode,
    Creates the dictionary that is to be sent to gempyp"""
    result = {}
    if not dv_obj.reporter.result_file_name:
        try:
            try:
                dv_obj.reporter.finalizeReport()   ## need to test
                if dv_obj.data.get("OUTPUT_FOLDER", dv_obj.default_report_path) is None:
                    os.makedirs(dv_obj.data.get("OUTPUT_FOLDER", dv_obj.default_report_path))
            except Exception as e:
                dv_obj.logger.info(traceback.format_exc())
            dv_obj.reporter.json_data = dv_obj.reporter.template_data.makeTestcaseReport()
            dv_obj.json_data = dv_obj.reporter.json_data
            result = dv_obj.reporter.serialize()
        except Exception as e:
            # dv_obj.logger.info(traceback.print_exc())
            traceback.print_exc()
    result = dv_obj.reporter.serialize()
    output = []
    tempdict = {} 
    unique_id = uuid.uuid4()
    try:
        if os.environ.get('unique_id'):
            unique_id = os.environ.get('unique_id')
            # unique_id = unique_id.split(dv_obj.data.get("ENV").upper()).strip("_")
    except Exception:
        traceback.print_exc()
    tc_run_id = f"{dv_obj.tcname}_{unique_id}"
    tempdict["tc_run_id"] = tc_run_id
    tempdict["name"] = result["NAME"]
    tempdict["category"] = dv_obj.category
    tempdict["status"] = result["STATUS"]
    tempdict["base_user"] = getpass.getuser()
    tempdict["invoke_user"] = dv_obj.data.get("INVOKE_USER")
    tempdict["machine"] = dv_obj.data.get("MACHINE")
    tempdict["product_type"] = "GEMPYP-DV"
    tempdict["steps"] = result["json_data"]['steps']
    tempdict["result_file"] = result["RESULT_FILE"]
    tempdict["start_time"] = result["START_TIME"]
    tempdict["end_time"] = result["END_TIME"]
    tempdict["ignore"] = False
    all_status = result["json_data"]["meta_data"][2]
    total = 0
    for key in all_status:
        total += all_status[key]
    result["json_data"]["meta_data"][2]["TOTAL"] = total

    # getting the log file ( the custom gempyp logger)
    try:
        s3_log_file_url = create_s3_link(url=upload_to_s3(DefaultSettings.urls["data"]["bucket-file-upload-api"], bridge_token=dv_obj.data.get("SUITE_VARS", None).get("bridge_token",None), username=dv_obj.data.get("SUITE_VARS", None).get("username",None), file=dv_obj.configData.get("log_path", dv_obj.configData.get("LOG_PATH","N.A")),tag="public")[0]["Url"])
        s3_log_file_url = f'<a href="{s3_log_file_url}" target=_blank>view</a>'
    except Exception:
        s3_log_file_url=None
    tempdict["log_file"] = dv_obj.configData.get("log_path","N.A")

    singleTestcase = {}
    singleTestcase["testcase_dict"] = tempdict
    singleTestcase["misc"] = result.get("MISC")
    singleTestcase["json_data"] = dv_obj.json_data
    singleTestcase["misc"]["log_file"] = s3_log_file_url
    output.append(singleTestcase)
    return output
