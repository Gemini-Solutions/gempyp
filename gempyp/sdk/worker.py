import os
import tempfile
import json
import configparser
import psutil
import sys
from gempyp.engine import dataUpload
from gempyp.reporter.reportGenerator import TemplateData
import logging
from gempyp.libs.common import *


def pid_running(pid):
    if not pid:
        return False
    if psutil.pid_exists(int(pid)):
        return True
    else:
        return False

def create_report(data, s_run_id):
     # read bridgetoken
    try:
        jewel=False
        config_file = configparser.ConfigParser()
        config_file.read("gempyp.conf")
        bridgetoken = config_file['ReportSetting'].get("jewel_bridge_token", None)
        username=config_file['ReportSetting'].get("jewel_user", None)
        if username and bridgetoken:
            jewel=True
    except Exception as e:
        bridgetoken = None
    data = json.loads(data)
    runBaseUrls(jewel,config_file['ReportSetting'].get("enter_point", None),username,bridgetoken)
    json_data = data[s_run_id]
    testcaseData = data["testcases"]
    output_folder = data["REPORT_LOCATION"]
    repJson = TemplateData().makeSuiteReport(json.dumps(json_data), testcaseData,output_folder,jewel)
    suite_data = json_data["suits_details"]
    suite_data["misc_data"] = data["misc_data"]
    username = suite_data["user"]
    del suite_data["testcase_details"]
    del suite_data["testcase_info"]
    dataUpload.sendSuiteData(json.dumps(suite_data), bridgetoken, username, mode="PUT")
    return output_folder


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
                        jewelLink = DefaultSettings.getUrls('jewel-url')
                        if jewelLink is not None:
                            jewel_link = f'{jewelLink}/#/autolytics/execution-report?s_run_id={s_run_id}&p_id={DefaultSettings.project_id}'
                            logging.info(f"Jewel link of gempyp report - {jewel_link}")
                        logging.info(f"Find Gempyp logs at - {s_run_id + '.log'}")
                        logging.info(f"Find Gempyp Report at - {output_file_path}")
                        logging.info(f"Jewel link of gempyp report - {jewel_link}")
                        # os.rename("logs.log",f"{s_run_id}.log")
                        os.kill(current_pid, 19)
                        sys.exit()
