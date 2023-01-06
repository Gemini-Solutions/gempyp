import os
import tempfile
import json
import configparser
import psutil
import sys
from gempyp.engine import dataUpload
from gempyp.reporter.reportGenerator import TemplateData
import logging


def pid_running(pid):
    if not pid:
        return False
    if psutil.pid_exists(int(pid)):
        return True
    else:
        return False

def create_report(data, s_run_id):

    data = json.loads(data)
    json_data = data[s_run_id]
    testcaseData = data["testcases"]
    output_folder = data["OUTPUT_FOLDER"]
    repJson, ouput_file_path = TemplateData().makeSuiteReport(json.dumps(json_data), testcaseData, output_folder)
    suite_data = json_data["suits_details"]
    suite_data["s_id"] = data["s_id"]
    suite_data["misc_data"] = data["misc_data"]
    username = suite_data["initiated_by"]
    del suite_data["testcase_details"]
    del suite_data["Testcase_Info"]

    # read bridgetoken
    try:
        config_file = configparser.ConfigParser()
        config_file.read("gempyp.conf")
        bridgetoken = config_file['ReportSetting'].get("bridge_token", None)
    except Exception as e:
        bridgetoken = None
    dataUpload.sendSuiteData(json.dumps(suite_data), bridgetoken, username, mode="PUT")
    return ouput_file_path


if __name__ == "__main__":
    while(True):
        if not pid_running(os.environ["PID"]):
            s_run_id = os.getenv("S_RUN_ID")
            if s_run_id:
                logging.basicConfig(level=logging.DEBUG)
                file_path = os.path.join(tempfile.gettempdir(), s_run_id + ".txt")
                if os.path.exists(file_path):
                    with open(file_path, "r+") as f:
                        data = str(f.read())
                        output_file_path = create_report(data, s_run_id)
                        # where to get this json data from
                        current_pid = os.getpid()
                        logging.info(f"Find Gempyp logs at - {s_run_id + '.txt'}")  ## replacing log with txt for UI compatibility
                        logging.info(f"Find Gempyp Report at - {output_file_path}")
                        os.rename("logs.txt",f"{s_run_id}.txt")
                        os.kill(current_pid, 19)
                        sys.exit()
