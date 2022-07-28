import os
import sys
import tempfile
import json
import time
import psutil
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


