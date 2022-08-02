import os
import tempfile
import json
import configparser
import psutil
from gempyp.engine import dataUpload
from gempyp.reporter.reportGenerator import templateData


def pid_running(pid):
    if not pid:
        return False
    if psutil.pid_exists(int(pid)):
        return True
    else:
        return False

def create_report(data, s_run_id):

    data = json.loads(data)
    jsonData = data[s_run_id]
    testcaseData = data["testcases"]
    output_folder = data["OUTPUT_FOLDER"]
    templateData().makeSuiteReport(json.dumps(jsonData), testcaseData, output_folder)
    suite_data = jsonData["Suite_Details"]
    suite_data["s_id"] = data["s_id"]
    suite_data["miscData"] = data["miscData"]
    username = suite_data["initiated_by"]
    del suite_data["TestCase_Details"]
    # read bridgetoken
    try:
        config_file = configparser.ConfigParser()
        config_file.read("gempyp.conf")
        bridgetoken = config_file['ReportSetting'].get("bridgetoken", None)
    except Exception as e:
        bridgetoken = None
    print(suite_data)
    dataUpload.sendSuiteData((suite_data), bridgetoken, username, mode="PUT")
    return 0


if __name__ == "__main__":
    while(True):
        if not pid_running(os.environ["PID"]):
            s_run_id = os.getenv("S_RUN_ID")
            if s_run_id:
                file_path = os.path.join(tempfile.gettempdir(), s_run_id + ".txt")
                if os.path.exists(file_path):
                    with open(file_path, "r+") as f:
                        data = str(f.read())
                        create_report(data, s_run_id)
                        # where to get this json data from
                        current_pid = os.getpid()
                        print(f"Find Gempyp logs at - {file_path.rsplit('.', 1)[0] + '.log'}")
                        os.kill(current_pid, 19)
