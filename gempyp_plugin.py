import pytest
import os
import sys
import uuid
import platform
import getpass
from gempyp.libs.common import *
from gempyp.engine.testData import TestData
from datetime import timezone
from gempyp.libs.enums.status import status
from gempyp.engine.baseTemplate import TestcaseReporter
from gempyp.engine.runner import getOutput
from gempyp.engine.engine import Engine
import tempfile
from gempyp.reporter.reportGenerator import TemplateData
from gempyp.libs.enums.status import status
from pathlib import Path


def pytest_addoption(parser):
    """Add support for the RP-related options.

    :param parser: Object of the Parser class
    """
    group = parser.getgroup('reporting')

    def add_shared_option(name, help_str, default=None, action='store'):
        """
        Add an option to both the command line and the .ini file.

        This function modifies `parser` and `group` from the outer scope.

        :param name:     name of the option
        :param help_str: help message
        :param default:  default value
        :param action:   `group.addoption` action
        """
        parser.addini(
            name=name,
            default=default,
            help=help_str,
        )
        group.addoption(
            '--{0}'.format(name.replace('_', '-')),
            action=action,
            dest=name,
            help='{help} (overrides {name} config option)'.format(
                help=help_str,
                name=name,
            ),
        )

    group.addoption(
        '--gempyp-enable',
        action='store_true',
        dest='gp_enable',
        default=False,
        help='Enable gempyp plugin'
    )
    add_shared_option(
        name='project-name',
        help_str='project name',
        default='Pytest integration with gempyp',
    )
    add_shared_option(
        name='environment',
        help_str='environment name',
        default='PROD',
    )
    add_shared_option(
        name='jewel-user',
        help_str='jewel user',
        default=None,
    )
    add_shared_option(
        name='jewel-bridge-token',
        help_str='jewel_bridge_token',
        default=None,
    )
    add_shared_option(
        name='enter-point',
        help_str='End point',
        default=None,
    )
    add_shared_option(
        name='mail-to',
        help_str='mail-to',
        default=None,
    )
    add_shared_option(
        name='mail-cc',
        help_str='mail-cc',
        default=None,
    )
    add_shared_option(
        name='mail-bcc',
        help_str='mail-bcc',
        default=None,
    )
    add_shared_option(
        name='report-name',
        help_str='report-name',
        default='SMOKE_TEST',
    )
    add_shared_option(
        name='s-run-id',
        help_str='s-run-id',
        default=os.getenv("S_RUN_ID"),
    )
    add_shared_option(
        name='report-location',
        help_str='report-location',
        default=None,
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if config.option.gp_enable:
        DATA = TestData()
        

        pytest.jewel_user,pytest.data=getTestcaseData(config)
        pytest.DATA=makeSuiteDetails(pytest.data,DATA)
    
        runBaseUrls(pytest.jewel_user,pytest.data["ENTER_POINT"],pytest.data["JEWEL_USER"],pytest.data["JEWEL_BRIDGE_TOKEN"])
        dataUpload.sendSuiteData((DATA.toSuiteJson()), pytest.data["JEWEL_BRIDGE_TOKEN"], pytest.data["JEWEL_USER"]) # check with deamon, should insert only once


def send_testcase_data(data,DATA,rep,s_run_id):
    reporter = TestcaseReporter(data["PROJECT_NAME"], rep.nodeid)
    if(rep.outcome=="passed"):
            testcaseStatus=status.PASS
    elif(rep.outcome=="failed"):
            testcaseStatus=status.FAIL
    else:
            testcaseStatus=status.INFO
    reporter.addRow( rep.nodeid, str(rep.longrepr), testcaseStatus)
    output = []
    reporter.finalizeReport()
    
    # create testcase reporter json
    reporter.json_data = reporter.template_data.makeTestcaseReport()
    # serializing data, adding suite data
    report_dict = reporter.serialize()

    report_dict["TESTCASEMETADATA"] = getMetaData(data)
    report_dict["config_data"] = getConfigData(data)
    # creating output json
    output.append(getOutput(report_dict))
    output[0]['testcase_dict']['run_type'], output[0]['testcase_dict']['run_mode'],output[0]['testcase_dict']['job_name'],output[0]['testcase_dict']['job_runid']="ON DEMAND","WINDOWS",None,None
    for i in output:
        i["testcase_dict"]["steps"] = i["json_data"]["steps"]
        dict_ = {}
        dict_["testcases"] = {}
        dict_["REPORT_LOCATION"] = os.getenv("REPORT_LOCATION")
        dict_["misc_data"] = {}
        tmp_dir = os.path.join(tempfile.gettempdir(), s_run_id + ".txt")

        DATA.testcase_details = DATA.testcase_details.append(
            i["testcase_dict"], ignore_index=True
        )   
        # self.DATA.testcaseDetails = pd.concat([self.DATA.testcaseDetails, pd.DataFrame(list(i["testcase_dict"].items()))])
        updateTestcaseMiscData(DATA,i["misc"], tc_run_id=i["testcase_dict"].get("tc_run_id"))
        suite_data = DATA.getJSONData()
        if isinstance(suite_data, str):
            suite_data = json.loads(suite_data)
        if isinstance(DATA.toSuiteJson(), str):
            suite_temp = json.loads(DATA.toSuiteJson())
        if not os.path.exists(tmp_dir):
            with open(tmp_dir, "w") as f:
                dict_[s_run_id] = updateSuiteData(suite_data)
                dict_["testcases"][i["testcase_dict"].get("tc_run_id")] = i["json_data"]
                f.write(json.dumps(dict_))
        else:
            with open(tmp_dir, "r+") as f:
                data = f.read()
                data = json.loads(data)
                data[s_run_id] = updateSuiteData(suite_data, data[s_run_id])
                data["testcases"][i["testcase_dict"].get("tc_run_id")] = i["json_data"]
                f.seek(0)
                f.write(json.dumps(data))
        updatedData=json.loads(DATA.totestcaseJson(i["testcase_dict"]["tc_run_id"].upper(), s_run_id))
        logging.info("TC_RUN_ID : "+i["testcase_dict"]["tc_run_id"].upper())
        dataUpload.sendTestcaseData(json.dumps(updatedData), pytest.jewel_bridge_token, pytest.jewel_user)  # instead of output, I need to pass s_run id and  tc_run_id




    
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call':
        duration = getattr(rep, "duration", None)
        data=pytest.data
        DATA=pytest.DATA
        s_run_id=data["S_RUN_ID"]
        pytest.jewel_bridge_token=data["JEWEL_BRIDGE_TOKEN"]
        pytest.jewel_user=data["JEWEL_USER"]
        send_testcase_data(data,DATA,rep,s_run_id)


def pytest_sessionfinish(session):
    s_run_id = os.getenv("S_RUN_ID")
    file_path = os.path.join(tempfile.gettempdir(), s_run_id + ".txt")
    if os.path.exists(file_path):
                    with open(file_path, "r+") as f:
                        data = str(f.read())
                        create_report(data, s_run_id)
                        # where to get this json data from
                        jewelLink = DefaultSettings.getUrls('jewel-url')
                        if jewelLink is not None:
                            jewel_link = f'{jewelLink}/#/autolytics/execution-report?s_run_id={s_run_id}&p_id={DefaultSettings.project_id}'
                            print(f"Jewel link of gempyp report - {jewel_link}")

def create_report(data, s_run_id):
     # read bridgetoken
    data = json.loads(data)
    json_data = data[s_run_id]
    jewel=pytest.jewel_user
    bridgetoken=pytest.jewel_bridge_token
    testcaseData = data["testcases"]
    suite_data = json_data["suits_details"]
    suite_data["misc_data"] = data["misc_data"]
    username = suite_data["user"]
    del suite_data["testcase_details"]
    del suite_data["testcase_info"]
    dataUpload.sendSuiteData(json.dumps(suite_data), bridgetoken, username, mode="PUT")



def updateSuiteData(current_data, old_data=None):
        """
        updates the suiteData after all the runs have been executed
        """
        start_time = current_data["suits_details"]["s_start_time"]
        end_time = current_data["suits_details"]['testcase_details'][0]["end_time"]
        testcaseData = current_data["suits_details"]['testcase_details']
        if old_data:
            testcaseData = (old_data["suits_details"]['testcase_details']
             + current_data["suits_details"]['testcase_details'])
            start_time = old_data["suits_details"]["s_start_time"]
        statusDict = {k.name: 0 for k in status}
        for i in testcaseData:
            statusDict[i["status"]] += 1
        # get the status count of the status
        SuiteStatus = status.FAIL.name

        # based on the status priority
        for s in status:
            if statusDict.get(s.name, 0) > 0:
                SuiteStatus = s.name

        current_data["suits_details"]["status"] = SuiteStatus
        current_data["suits_details"]['testcase_details'] = testcaseData
        current_data["suits_details"]["s_start_time"] = start_time
        current_data["suits_details"]["s_end_time"] = end_time
        count = 0
        for key in list(statusDict.keys()):
            if statusDict[key] == 0:
                del statusDict[key]
            else:
                count += statusDict[key]
        statusDict["total"] = count
        current_data["suits_details"]["expected_testcases"]=count
        current_data["suits_details"]["testcase_info"] = statusDict

        return current_data
        
def getMetaData(data):
        data = {
            'PROJECT_NAME': data["PROJECT_NAME"], 
            'ENVIRONMENT': data["ENVIRONMENT"], 
            'S_RUN_ID': data["S_RUN_ID"], 
            'USER': data["JEWEL_USER"], 
            'MACHINE': data["MACHINE"], 
            'REPORT_LOCATION': data["REPORT_LOCATION"],
            'SUITE_VARS': data.get("SUITE_VARS", {}),
            'INVOKE_USER': os.getenv("INVOKEUSER", data["JEWEL_USER"])}
        return data

def getConfigData(data):
        data = {'NAME': data["PROJECT_NAME"], 'CATEGORY': 'External','LOGGER': ""}
        return data

def updateTestcaseMiscData(DATA, misc, tc_run_id):
        """
        updates the misc data for the testcases
        """
        miscList = []

        for misc_data in misc:
            temp = {}
            # storing all the key in upper so that no duplicate data is stored
            temp["key"] = misc_data.upper()
            temp["value"] = misc[misc_data]
            temp["run_id"] = tc_run_id
            temp["table_type"] = "TESTCASE"
            miscList.append(temp)

        DATA.misc_details = DATA.misc_details.append(
            miscList, ignore_index=True
        )

def getTestcaseData(config):
        jewel_user=False
        data = {}
        projectName = data["PROJECT_NAME"] =config.getini("project-name")
        env = data["ENVIRONMENT"] = config.getini("environment")
        testcaseName = data["NAME"] = None
        data["JEWEL_USER"] = config.getini("jewel-user")
        data["JEWEL_BRIDGE_TOKEN"] = config.getini("jewel-bridge-token")
        data["REPORT_LOCATION"] = config.getini("report-location")
        data["MACHINE"] = platform.node()
        data["MAIL_TO"] = config.getini("mail-to")
        data["MAIL_CC"] = config.getini("mail-cc")
        data["MAIL_BCC"] = config.getini("mail-bcc")
        data["ENTER_POINT"]=config.getini("enter-point")
        if data["JEWEL_USER"] and data["JEWEL_BRIDGE_TOKEN"]:
            jewel_user=True
        report_type = data["REPORT_NAME"] = config.getini("report-name")
        if not config.getini("s-run-id"):
            s_run_id=data["S_RUN_ID"] = data["PROJECT_NAME"] + "_" + data["ENVIRONMENT"] + "_" + str(uuid.uuid4())
            os.environ["S_RUN_ID"] = s_run_id
        else:
            s_run_id = data["S_RUN_ID"] = config.getini("s-run-id")
        
        return jewel_user,data


def makeSuiteDetails(data,DATA):
        """
        making suite Details 
        """
        
        run_mode = "LINUX_CLI"
        if os.name == 'nt':
            run_mode = "WINDOWS"
        Suite_details = {
            "s_run_id": data["S_RUN_ID"],
            "s_start_time": datetime.now(timezone.utc),
            "s_end_time": None,
            "s_id": data.get("S_ID", "test_id"),
            "status": status.EXE.name,
            "project_name": data["PROJECT_NAME"],
            "report_name": data["REPORT_NAME"],
            "run_type": "ON DEMAND",
            "user": data["JEWEL_USER"],
            "env": data["ENVIRONMENT"],
            "machine": data["MACHINE"],
            "run_mode": run_mode,
            "os": platform.system().upper(),
            "meta_data": [],
            "testcase_info": None,
            "expected_testcases":1,
            "framework_name": "GEMPYP",
        }
        DATA.suite_detail = DATA.suite_detail.append(
            Suite_details, ignore_index=True
        )
        return DATA




