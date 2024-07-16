from pathlib import Path
import sys
import os
import platform
import getpass
import traceback
from multiprocessing import Pool
from typing import Dict, List, Tuple, Type
from unittest import TestCase
import uuid
from datetime import datetime, timezone
from gempyp.config.baseConfig import AbstarctBaseConfig
# from gempyp.engine.baseTemplate import TestcaseReporter as Base
from gempyp.engine.testData import TestData
from gempyp.libs.enums.status import status
from gempyp.libs.enums.run_types import RunTypes
from gempyp.reporter.reportGenerator import TemplateData
from gempyp.libs import common
from gempyp.engine.runner import testcaseRunner
from gempyp.config import DefaultSettings
import logging
from gempyp.libs.logConfig import my_custom_logger, LoggingConfig
from gempyp.engine import dataUpload
from gempyp.pyprest.pypRest import PypRest
import smtplib
from gempyp.dv.dvRunner import DvRunner
from gempyp.jira.jiraIntegration import jiraIntegration
from multiprocessing import Process, Pipe
from gempyp.libs.gem_s3_common import upload_to_s3, create_s3_link, uploadToS3
from gempyp.libs.common import *
import re
from importlib.metadata import version


def executorFactory(data: Dict, conn=None, custom_logger=None) -> Tuple[List, Dict]:
    """
    calls the differnt executors method based on testcase type e.g. gempyp,pyprest,dvm
    Takes single testcase data as input
    """
    logging.info("--------- In Executor Factory ----------\n")
    if custom_logger == None:
        testcase_name = data['config_data'].get('NAME', None)
        testcase_name = re.sub('[^A-Za-z0-9]+', '_', testcase_name)
        log_path = os.path.join(os.environ.get('TESTCASE_LOG_FOLDER'), testcase_name + '_'
                                + os.environ.get('unique_id') + '.txt')  # replacing log with txt for UI compatibility
        if len(log_path) > 240:
            log_path = os.path.join(os.environ.get(
                'TESTCASE_LOG_FOLDER'), str(uuid.uuid4()) + '.txt')
        custom_logger = my_custom_logger(log_path)
        LoggingConfig(log_path)
    data['config_data']['LOGGER'] = custom_logger
    if 'log_path' not in data['config_data']:
        data['config_data']['LOG_PATH'] = log_path

    engine_control = {
        "pyprest": {"class": PypRest, "classParam": data, "function": "restEngine"},
        "dv": {"class": DvRunner, "classParam": data, "function": "dvEngine"},
        "gempyp": {"function": testcaseRunner, "functionParam": data}
    }
    _type = data.get("config_data").get("TYPE", "GEMPYP") if data.get(
        "config_data").get("TYPE", None) else "GEMPYP"
    dv = ["data validator", "dv", "datavalidator", "dvalidator"]
    if _type in dv:
        _type = "dv"

    _type_dict = engine_control[_type.lower()]
    custom_logger.info(f"Starting {_type} testcase")

    if _type_dict.get("class", None):
        # need to make it generic for functionParam too
        data = getattr(_type_dict["class"](
            _type_dict['classParam']), _type_dict['function'])()
    else:
        # we need to dissolve this else condition too somehow
        data = _type_dict["function"](_type_dict["functionParam"])
    if conn == None:
        return data
    else:
        conn.send([data])
        conn.close()


class Engine:
    def __init__(self, params_config):
        """
        constructor used to  call run method
        takes config as input
        """
        # logging.basicConfig()
        # logging.root.setLevel(logging.DEBUG)
        sorted_config = self.sortTestcase(getattr(params_config, "_CONFIG"))
        setattr(params_config, "_CONFIG", sorted_config)
        self.run(params_config)

    def run(self, params_config: Type[AbstarctBaseConfig]):
        """
        main method to call other methods that are required for report generation
        takes config as input
        """
        logging.info("Engine Started")
        # initialize the data class

        self.DATA = TestData()
        # get the env for the engine Runner
        # self.ENV = os.getenv("appenv", "BETA").upper()
        # initial SETUP
        self.setUP(params_config)
        self.makeSuiteDetails()
        # handle case of dependency
        validateZeroTestcases(self.CONFIG.getTestcaseLength())
        runBaseUrls(self.jewel_user, self.base_url, self.username,
                    self.bridgetoken)  # retrying to run Base Urls
        self.DATA.validateSrunidInDB(
            self.jewel_user, self.s_run_id, self.username, self.bridgetoken)
        self.makeOutputFolder()
        self.start()

        if (self.jewel_user and DefaultSettings.apiSuccess):
            self.DATA.retryUploadSuiteData(self.bridgetoken, self.username)
        jewel, failed_Utestcases = self.DATA.retryUploadTestcases(
            self.s_run_id, self.bridgetoken, self.username, self.ouput_folder)
        self.updateSuiteData()
        unuploaded_path = None
        if dataUpload.suite_uploaded and DefaultSettings.apiSuccess:
            dataUpload.sendSuiteData(self.DATA.toSuiteJson(
            ), self.bridgetoken, self.username, mode="PUT")

            if self.skip_jira == 0:
                jira_id = jiraIntegration(self.s_run_id, self.jira_email, self.jira_access_token, self.jira_project_id, self.project_env, self.jira_workflow,
                                        self.jira_title, self.bridgetoken, self.username, self.report_name)  # adding title  ######################### post 1.0.4
                if jira_id is not None:
                    self.DATA.suite_detail.at[0, "meta_data"].append(
                        {"Jira_id": jira_id})
            # # dataUpload.sendSuiteData(self.DATA.toSuiteJson(), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"], mode="PUT")
        else:
            unuploaded_path = self.DATA.WriteSuiteFile(
                self.base_url, self.ouput_folder, self.username, self.bridgetoken)

        if ("EMAIL_TO" in self.PARAMS.keys()):
            sendMail(self.s_run_id, self.mail, self.bridgetoken, self.username)

        self.repJson = TemplateData().makeSuiteReport(self.DATA.getJSONData(),
                                                    self.testcase_data, self.ouput_folder, self.jewel_user)
        TemplateData().repSummary(self.repJson, jewel, unuploaded_path, self.testcase_log_folder,
                                self.complete_logs, self.bridgetoken, self.username, self.suite_log_file)

    def makeOutputFolder(self):
        """
        make outputFolder for report named as gempyp_reports in user home directory if not given by the user and makes log fplder for log files
        if given by user than set user given path for reports file   
        """

        logging.info("---------- Making output folders -------------")
        report_folder_name = f"{self.project_name}_{self.project_env}"
        if self.report_name:
            report_name = "_".join(self.report_name.split())
            report_folder_name = report_folder_name + f"_{report_name}"
        date = datetime.now().strftime("%Y_%b_%d_%H%M%S_%f")
        report_folder_name = report_folder_name + f"_{date}"
        try:
            if "REPORT_LOCATION" in self.PARAMS and self.PARAMS["REPORT_LOCATION"]:
                self.ouput_folder = os.path.join(
                    self.PARAMS["REPORT_LOCATION"], report_folder_name
                )
            else:
                home = str(Path.home())
                self.ouput_folder = os.path.join(
                    home, "gempyp_reports", report_folder_name
                )
        except Exception:
            temp = str(tempfile.gettempdir())
            self.ouput_folder = os.path.join(
                temp, "gempyp_reports", report_folder_name
            )
        os.makedirs(self.ouput_folder)
        self.testcase_folder = os.path.join(self.ouput_folder, "testcases")
        os.makedirs(self.testcase_folder)
        self.testcase_log_folder = os.path.join(self.ouput_folder, "logs")
        os.environ['TESTCASE_LOG_FOLDER'] = self.testcase_log_folder
        os.makedirs(self.testcase_log_folder)
        self.complete_logs = os.path.join(
            self.testcase_log_folder, self.s_run_id + '.txt')

    def verify(self, value):
        if (re.search(r'[^a-zA-Z0-9_ .-]', value)):
            logging.info(
                "Some Error From the Client Side. May be s_run_id, project_name or ENV is not in a correct format")
            sys.exit()
        else:
            return value

    def setUP(self, config: Type[AbstarctBaseConfig]):
        """

        assigning values to some attributes which will be used in method makeSuiteDetails

        """

        self.PARAMS = config.getSuiteConfig()
        self.suite_log_file = config.getLogFilePath()
        self.ENV = os.getenv("appenv", "BETA").upper()

        #checking if url is present in file and calling get api
        self.CONFIG = config

        self.testcase_data = {}

        self.total_runable_testcase = config.total_yflag_testcase

        self.machine = platform.node()
        # creating job_name variable to set job name from suite tags reason:- facing issue on lambda side 
        self.job_name = self.PARAMS.get("JEWEL_JOB",None)
        
        self.user = self.PARAMS.get("JEWEL_USER", getpass.getuser())
        self.username = self.PARAMS.get("JEWEL_USER", None)
        self.bridgetoken = self.PARAMS.get("JEWEL_BRIDGE_TOKEN", None)
        self.base_url = self.PARAMS.get("ENTER_POINT", None)
        self.autoKill = self.PARAMS.get("AUTO_KILL", 'y')
        if self.autoKill.lower() not in ['y', 'n', "true", "false"]:
            self.autoKill = 'y'
            logging.info(
                "Auto kill value given by user is not accurate, keeping it as Y")
        # INVOKEUSER can be set as environment variable from anywhere.
        self.invoke_user = os.getenv("INVOKEUSER", self.user)
        self.current_dir = os.getcwd()

        self.platform = platform.system()

        self.start_time = datetime.now(timezone.utc)
        self.skip_jira = 0
        try:
            self.jira_email = self.PARAMS.get("JIRA_EMAIL", None)
            self.jira_access_token = self.PARAMS.get("JIRA_ACCESS_TOKEN", None)
            self.jira_project_id = self.PARAMS.get("JIRA_PROJECT_ID", None)
            self.jira_workflow = self.PARAMS.get("JIRA_WORKFLOW", None)
            # adding title  ######################### post 1.0.4
            self.jira_title = self.PARAMS.get("JIRA_TITLE", None)
            if self.jira_access_token is None and self.jira_email is None:
                self.skip_jira = 1
        except Exception as e:
            pass

        mail_items = {"to": "EMAIL_TO", "cc": "EMAIL_CC", "bcc": "EMAIL_BCC"}
        self.mail = {key: common.parseMails(self.PARAMS.get(
            value, None)) for key, value in mail_items.items()}

        self.project_name = self.verify(self.PARAMS["PROJECT_NAME"])
        self.project_env = self.verify(self.PARAMS["ENVIRONMENT"])
        self.report_name = strValidation(self.PARAMS.get("REPORT_NAME"))
        self.unique_id = self.PARAMS["UNIQUE_ID"]
        self.user_suite_variables = self.PARAMS.get("SUITE_VARS", {})
        self.user_global_variables = self.PARAMS.get("GLOBAL_VARIABLES", {})
        self.jewel_run = False
        self.jewel_user = False
        self.s3_url = ""
        if self.bridgetoken and self.username:
            self.user_suite_variables["bridge_token"] = self.bridgetoken
            self.user_suite_variables["username"] = self.username
            self.jewel_user = True

        runBaseUrls(self.jewel_user, self.base_url, self.username,
                    self.bridgetoken)  # Run base Urls
        if self.jewel_user:
            # trying first run of base url api in case of api failure

            if self.PARAMS.get("S_ID", None):
                self.jewel_run = True
            else:
                try:
                    if DefaultSettings.apiSuccess:
                        self.s3_url = upload_to_s3(DefaultSettings.urls["data"]["bucket-file-upload-api"],
                                                bridge_token=self.bridgetoken, username=self.username, file=self.PARAMS["config"])[0]["Url"]
                        logging.info("S3 Url: " + str(self.s3_url))
                    else:
                        self.s3_url = self.PARAMS["config"]
                except Exception as e:
                    logging.info(e)

    def makeSuiteDetails(self):
        """
        making suiteDetails dictionary and assign it to DATA.suiteDetail 
        """
        if "S_RUN_ID" in self.PARAMS:
            self.s_run_id = self.verify(self.PARAMS["S_RUN_ID"])
        else:
            if not self.unique_id:
                self.unique_id = uuid.uuid4()
            self.s_run_id = f"{self.project_name}_{self.project_env}_{self.unique_id}"
            self.s_run_id = self.s_run_id.upper()
        logging.info("S_RUN_ID: {}".format(self.s_run_id))
        package_name = "gempyp"
        try:
            version1 = version(package_name)
        except Exception:
            version1 = None

        # If package is not installed, try to get version from setup.py
        if version1 is None:
            version1 = self.get_version_from_setup()
        suite_details = {
            "s_run_id": self.s_run_id,
            "s_start_time": self.start_time,
            "s_end_time": None,
            "s_id": self.PARAMS.get("S_ID", "test_id"),
            "status": status.EXE.name,
            "project_name": self.project_name,
            "report_name": self.report_name,  # earlier it was report info
            "user": self.user,
            "env": self.project_env,
            "machine": self.machine,
            "framework_version": version1,
            "os": platform.system().upper()+" "+platform.version().split(".")[0],
            "meta_data": [],
            "expected_testcases": self.total_runable_testcase,
            "testcase_info": None,
            "framework_name": "GEMPYP",
            "autoKill": self.autoKill.lower()
        }
        self.DATA.suite_detail = self.DATA.suite_detail.append(
            suite_details, ignore_index=True
        )

    def get_version_from_setup(self):
        try:
            with open('setup.py', 'r') as setup_file:
                content = setup_file.read()
                # Extract version using regular expression
                match = re.search(r"version=['\"](.*?)['\"]", content)
                if match:
                    return match.group(1)
        except FileNotFoundError:
            pass  # Handle the case when setup.py is not found
        except Exception as e:
            print(f"An error occurred while reading setup.py: {e}")

        return None

    def start(self):
        """
        check the mode and start the testcases accordingly e.g.optimize,parallel
        check the mode and start the testcases accordingly e.g.optimize,parallel
        """
        try:
            if self.PARAMS["MODE"].upper() == "SEQUENCE":
                self.startSequence()
            elif self.PARAMS["MODE"].upper() == "OPTIMIZE" or self.PARAMS.get("MODE", None) is None:
                self.startParallel()
            else:
                raise TypeError("mode can only be sequence or optimize")

        except Exception as e:
            logging.error(traceback.format_exc())
            try:
                self.DATA.suite_detail.at[0, "meta_data"].append(
                    {"REASON OF FAILURE": str(e)})
                self.updateSuiteData()
            except Exception as err:
                logging.error(traceback.format_exc())
                logging.info(err)
            if DefaultSettings.apiSuccess:
                dataUpload.sendSuiteData(
                    (self.DATA.toSuiteJson()), self.bridgetoken, self.username)
            else:
                dataUpload.suite_data.append(self.DATA.toSuiteJson())
            # need to add reason of failure of the suite in misc

    def updateSuiteData(self):
        """
        updates the suiteData after all the runs have been executed
        """

        # get the status count of the status
        status_dict = self.DATA.testcase_details["status"].value_counts(
        ).to_dict()
        total = sum(status_dict.values())
        status_dict["TOTAL"] = total
        unsorted_dict = status_dict
        sorted_dict = self.totalOrder(unsorted_dict)
        status_dict = sorted_dict
        # status_dict = dict( sorted(status_dict.items(), key=lambda x: x[0].lower(), reverse=True) )
        Suite_status = status.FAIL.name

        # based on the status priority
        for s in status:
            if status_dict.get(s.name, 0) > 0:
                Suite_status = s.name
                break
        stop_time = (
            self.DATA.testcase_details["end_time"].sort_values(
                ascending=False).iloc[0]
        )
        self.DATA.suite_detail.at[0, "status"] = Suite_status
        self.DATA.suite_detail.at[0, "s_end_time"] = stop_time
        self.DATA.suite_detail.at[0, "testcase_info"] = status_dict
        if self.jewel_run is True:
            self.DATA.suite_detail.at[0, "meta_data"].append(
                {"S_ID": self.PARAMS["S_ID"]})
        else:
            self.DATA.suite_detail.at[0, "meta_data"].append(
                {"CONFIG_S3_URL": self.s3_url})

    def startSequence(self):
        """
        start calling executoryFactory() for each testcase one by one according to their dependency
        at last of each testcase calls the update_df() 
        """
        response = False
        for testcases in self.getDependency(self.CONFIG.getTestcaseConfig()):
            if response:
                break
            for testcase in testcases:
                passedDependency = self.isDependencyPassed(testcase)
                product_type = {'dv': "GEMPYP-DV",
                                    "pyprest": "GEMPYP-PR", "gempyp": "GEMPYP"}
                dependency_error = {
                    "message": "dependency failed",
                    "testcase": testcase["NAME"],
                    "category": testcase.get("CATEGORY", None),
                    "product_type": product_type.get(testcase.get("TYPE", None), testcase.get("TYPE", None)),
                }
                if passedDependency == 'true':
                    data = self.getTestcaseData(testcase['NAME'])
                    testcase_name = data['config_data'].get('NAME', None)
                    testcase_name = re.sub('[^A-Za-z0-9]+', '_', testcase_name)
                    log_path = os.path.join(self.testcase_log_folder,
                                            testcase_name+'_'+self.CONFIG.getSuiteConfig()['UNIQUE_ID'] + '.txt')  # ## replacing log with txt for UI compatibility
                    if len(log_path) > 240:
                        log_path = os.path.join(os.environ.get(
                            'TESTCASE_LOG_FOLDER'), str(uuid.uuid4()) + '.txt')
                    custom_logger = my_custom_logger(log_path)
                    data['config_data']['log_path'] = log_path
                    conn = None
                    output, error = executorFactory(data, conn, custom_logger)
                    if output is not None and output[0]["GLOBAL_VARIABLES"].get("UPDATED_GLOBAL_VARS", None) is not None:
                        key_list = output[0]["GLOBAL_VARIABLES"]["UPDATED_GLOBAL_VARS"]
                        for key in key_list:
                            logging.info(
                                " Updating global variables values after testcase execution -- {k}".format(k=key))
                            self.user_global_variables[key] = output[0]["GLOBAL_VARIABLES"][key]
                    response = self.update_df(output, error)
                    if response:
                        break
                elif passedDependency == 'err':
                    dependency_error["status"] = status.ERR.name
                    self.update_df(None, dependency_error)
                elif passedDependency == 'fail':
                    dependency_error["status"] = status.ERR.name
                    self.update_df(None, dependency_error)

    def startParallel(self):
        """
        start calling executorFactory for testcases in parallel according to their drependency 
        at last of each testcase calls the update_df()
        """
        pool = None
        try:

            threads = self.PARAMS.get("THREADS", DefaultSettings.THREADS)
            try:
                threads = int(threads)
            except:
                threads = DefaultSettings.THREADS
            # pool = Pool(threads)
            response = False
            for testcases in self.getDependency(self.CONFIG.getTestcaseConfig()):
                if response:
                    break

                # create a list to keep connections
                if len(testcases) == 0:
                    raise Exception("No testcase to run")
                pool_list = []
                for testcase in testcases:
                    # only append testcases whose dependency are passed otherwise just update the databasee
                    passedDependency = self.isDependencyPassed(testcase)
                    product_type = {'dv': "GEMPYP-DV",
                                        "pyprest": "GEMPYP-PR", "gempyp": "GEMPYP"}
                    dependency_error = {
                        "message": "dependency failed",
                        "testcase": testcase["NAME"],
                        "category": testcase.get("CATEGORY", None),
                        "product_type": product_type.get(testcase.get("TYPE", None), testcase.get("TYPE", None)),
                        "status": status.ERR.name
                    }
                    if passedDependency == 'true':
                        pool_list.append(
                            self.getTestcaseData(testcase.get("NAME")))
                    elif passedDependency == 'err':
                        dependency_error["status"] = status.ERR.name
                        self.update_df(None, dependency_error)
                    elif passedDependency == 'fail':
                        dependency_error["status"] = status.FAIL.name
                        self.update_df(None, dependency_error)


                if len(pool_list) == 0:
                    continue

                # obj = Semaphore(8)
                splitedSize = threads
                a_splited = [pool_list[x:x+splitedSize]
                            for x in range(0, len(pool_list), splitedSize)]
                for chunk_list in a_splited:
                    if response:
                        break
                    processes = []
                    parent_connections = []
                    for testcase in chunk_list:
                        testcase["default_urls"] = DefaultSettings.urls
                        parent_conn, child_conn = Pipe()
                        parent_connections.append(parent_conn)

                # create the process, pass instance and connection
                        custom = None
                        process = Process(target=executorFactory, args=(
                            testcase, child_conn, custom))
                        processes.append(process)
                # runs the testcase in parallel here
                    instances_total = []

                    # print(a_splited)
                    # for i in a_splited:
                    for process in processes:
                        process.start()
                    for parent_connection in parent_connections:

                        instances_total.append(parent_connection.recv()[0])
                        if len(instances_total) > 0:
                            row = instances_total[-1]
                            if not row or len(row) < 2:
                                raise Exception(
                                    "Some error occurred while running the testcases"
                                )
                            output = row[0]

                            error = row[1]
                            if error:
                                logging.error(
                                    f"Error occurred while executing the testcase: {error['testcase']}"
                                )
                                logging.error(f"message: {error['message']}")

                            if output is not None and output[0]["GLOBAL_VARIABLES"].get("UPDATED_GLOBAL_VARS", None) is not None:
                                key_list = output[0]["GLOBAL_VARIABLES"]["UPDATED_GLOBAL_VARS"]
                                for key in key_list:
                                    logging.info(
                                        " Updating global variables values after testcase execution -- {k}".format(k=key))
                                    self.user_global_variables[key] = output[0]["GLOBAL_VARIABLES"][key]

                            response = self.update_df(output, error)
                    

                    for process in processes:
                        process.join()
        except Exception:
            logging.error(traceback.format_exc())

    def update_df(self, output: List, error: Dict):
        """
        updates the testcase data in the dataframes of testData.py
        also upload testcasedata to db

        """
        try:
            if error:
                output = self.getErrorTestcase(
                    error["message"],
                    error["testcase"],
                    error.get("category"),
                    error.get("product_type"),
                    error.get('log_path', None),
                    error.get('status', status.ERR)
                )
                output = [output]
            if 'json_data' in output[0]:
                unsorted_dict = output[0]['json_data']['meta_data'][2]
                sorted_dict = self.totalOrder(unsorted_dict)
                output[0]['json_data']['meta_data'][2] = sorted_dict

            output[0]['testcase_dict']['run_type'], output[0]['testcase_dict']['run_mode'], output[0][
                'testcase_dict']['job_name'], output[0]['testcase_dict']['job_runid'] = self.set_run_type_mode()
            for i in output:
                if 'json_data' in i:
                    i["testcase_dict"]["steps"] = i["json_data"]["steps"]
                else:
                    i["testcase_dict"]["steps"] = self.build_err_step_case()

                testcase_dict = i["testcase_dict"]
                try:
                    """ update suite vars here from testcase_dict["suite_variables"] append it in the suite vars of _config"""

                    self.user_suite_variables.update(
                        i.get("suite_variables", {}))

                    self.testcase_data[testcase_dict.get(
                        "tc_run_id")] = i["json_data"]
                except Exception as e:
                    logging.error(e)
                self.DATA.testcase_details = self.DATA.testcase_details.append(
                    testcase_dict, ignore_index=True
                )
                self.updateTestcaseMiscData(
                    i["misc"], tc_run_id=testcase_dict.get("tc_run_id")
                )
                if (self.jewel_user and dataUpload.suite_uploaded):
                    response = dataUpload.sendTestcaseData((self.DATA.totestcaseJson(testcase_dict.get(
                        "tc_run_id").upper(), self.s_run_id)), self.bridgetoken, self.username)
                    return True if response == 412 else False

                else:
                    dataUpload.not_uploaded.append((self.DATA.totestcaseJson(
                        testcase_dict.get("tc_run_id").upper(), self.s_run_id)))

        except Exception as e:
            traceback.print_exc()
            logging.error("in update_df: {e}".format(e=e))

    def build_err_step_case(self):
        step = [{'Step Name': 'Starting Test', 'Step Description':
                'Either the testcase is inappropriate or some error occurred while executing the test. Please recheck', 'status': 'ERR'}]

        return step

    def raise_exception(self, name):
        raise ValueError("{} does not exist".format(name))

    def set_run_type_mode(self):
        try:
            run_type=run_mode=job_name=job_runid=None
            mappings = {('JEWEL'): { 
                'run_type': 'Scheduled', 
                'run_mode': 'JEWEL_SCHEDULER',
                'job_name': lambda: os.environ.get('JEWEL_JOB',None), 
                'job_runid': 'NONE' 
            },
                ('SCHEDULER_TOOL'): {
                'run_type': 'Scheduled',
                'run_mode': lambda: os.environ.get('SCHEDULER_TOOL'),
                'job_name': lambda: os.environ.get('SCHEDULER_JOB') if os.environ.get('SCHEDULER_JOB', None) else self.raise_exception("Schedular job"),
                'job_runid': lambda: os.environ.get('SCHEDULER_RUNNUM') if os.environ.get('SCHEDULER_RUNNUM', None) else self.raise_exception("Schedular rennum")
            },
                ('CI_CD_CT_TOOL'): {
                'run_type': 'CI-CD-CT',
                'run_mode': lambda: os.environ.get('CI_CD_CT_TOOL') if os.environ.get('CI_CD_CT_TOOL', None) else self.raise_exception("CI_CD_CT_TOOL"),
                'job_name': lambda: os.environ.get('CI_CD_CT_JOB') if os.environ.get('CI_CD_CT_JOB', None) else self.raise_exception('CI_CD_CT_JOB'),
                'job_runid': lambda: os.environ.get('CI_CD_CT_RUNNUM') if os.environ.get('CI_CD_CT_RUNNUM', None) else self.raise_exception('CI_CD_CT_RUNNUM')
            },
                ('AUTO_JOB_NAME'): {
                'run_type': 'Scheduled',
                'run_mode': 'Autosys',
                'job_name': lambda: os.environ.get('AUTOSERV') + '.' + os.environ.get('AUTO_JOB_NAME') if os.environ.get('AUTOSERV', None) and os.environ.get('AUTO_JOB_NAME', None) else self.raise_exception("AUTOSERV or AUTO_JOB_NAME"),
                'job_runid': lambda: os.environ.get('AUTO_JOBID') if os.environ.get('AUTO_JOBID', None) else self.raise_exception("AUTO_JOBID")
            },
                ('JENKINS_URL'): {
                'run_type': lambda: 'Scheduled' if os.environ.get('BUILD_CAUSE') == 'TIMERTRIGGER' else 'CI-CD-CT' if os.environ.get('BUILD_CAUSE') == 'SCMTRIGGER' else 'On Demand',
                'run_mode': 'Jenkins',
                'job_name': lambda: os.environ.get('JOB_DISPLAY_URL') if os.environ.get('JOB_DISPLAY_URL', None) else self.raise_exception("JOB_DISPLAY_URL"),
                'job_runid': lambda: os.environ.get('BUILD_URL') if os.environ.get('BUILD_URL', None) else self.raise_exception("BUILD_URL")}
            }
            # Try to match the environment variables to one of the defined mappings
            for env_vars, mapping in mappings.items():
                if (env_vars in os.environ):
                    # Evaluate the values that require computation (i.e. lambda functions)
                    run_type = mapping['run_type']() if callable(
                        mapping['run_type']) else mapping['run_type']
                    run_mode = mapping['run_mode']() if callable(
                        mapping['run_mode']) else mapping['run_mode']
                    job_name = mapping['job_name']() if callable(
                        mapping['job_name']) else mapping['job_name']
                    job_runid = mapping['job_runid']() if callable(
                        mapping['job_runid']) else mapping['job_runid']
                    break
                else:
                    # If no mapping is found, set default values
                    run_type = 'On Demand'
                    # run_mode = os.name
                    run_mode = platform.uname().system
                    job_name = 'NONE'
                    job_runid = 'NONE'
        except ValueError as e:
            logging.error(e)
        return run_type, run_mode, job_name, job_runid

    def getErrorTestcase(
        self,
        message: str,
        testcase_name: str,
        category: str = None,
        product_type: str = None,
        log_path: str = None,
        status: str = None
    ) -> Dict:
        """
        store the data of failed testcase and return it as a dict to update_df
        take message for error as input
        """

        result = {}
        testcase_dict = {}
        misc = {}
        if not self.unique_id:
            self.unique_id = uuid.uuid4()
        # testcase should not be testcase + s_run_id
        tc_run_id = f"{testcase_name}_{self.unique_id}"

        tc_run_id = tc_run_id.upper()
        testcase_dict["tc_run_id"] = tc_run_id
        testcase_dict["status"] = status
        testcase_dict["start_time"] = datetime.now(timezone.utc)
        testcase_dict["end_time"] = datetime.now(timezone.utc)
        testcase_dict["name"] = testcase_name
        testcase_dict["ignore"] = False
        if category:
            testcase_dict["category"] = category
        s3_log_file_url = log_path
        if self.jewel_user:
            try:
                s3_log_file_url= uploadToS3(DefaultSettings.urls["data"].get("pre-signed",None), bridge_token=self.bridgetoken, username=self.username, file=log_path,tag="protected",folder="logs",s_run_id=self.s_run_id)[0]
                # s3_log_file_url = f'<a href="{s3_log_file_url}" target=_blank>view</a>'
            except Exception as e:
                logging.info(e)
        testcase_dict["log_file"] = log_path
        testcase_dict["result_file"] = None
        testcase_dict["base_user"] = getpass.getuser()
        testcase_dict["invoke_user"] = self.invoke_user
        testcase_dict["machine"] = self.machine
        # testcase_dict["response_time"]="{0:.{1}f} sec(s)".format((testcase_dict["end_time"]-testcase_dict["start_time"]).total_seconds(),2)
        if product_type:
            testcase_dict["product_type"] = product_type
        result["testcase_dict"] = testcase_dict
        misc["REASON OF FAILURE"] = message
        result["misc"] = misc
        result["misc"]["log_file"] = s3_log_file_url
        # result["json_data"]["meta_data"][2]["TOTAL"] = total   # we can not get dummy data because here testcase does not exist
        return result

    def updateTestcaseMiscData(self, misc: Dict, tc_run_id: str):
        """
        updates the misc data for the testcases in testData.py
        accept miscellaneous rows and tc_run_id as parameters
        """
        misc_list = []

        for misc_data in misc:
            temp = {}
            # storing all the key in upper so that no duplicate data is stored
            temp["key"] = misc_data.upper()
            temp["value"] = misc[misc_data]
            temp["run_id"] = tc_run_id
            temp["table_type"] = "TESTCASE"
            misc_list.append(temp)

        self.DATA.misc_details = self.DATA.misc_details.append(
            misc_list, ignore_index=True
        )

    def getTestcaseData(self, testcase: str) -> Dict:
        """
        taking argument as the testcase name and  return dictionary containing information about testCase
        """
        data = {}
        list_subtestcases = []
        data["config_data"] = self.CONFIG.getTestcaseData(testcase)
        if ("SUBTESTCASES" in data["config_data"].keys()):
            for key1 in data["config_data"]["SUBTESTCASES"].split(","):
                list_subtestcases.append(self.CONFIG.getSubTestcaseData(key1))
            data["config_data"]["SUBTESTCASES_DATA"] = list_subtestcases
        data["PROJECT_NAME"] = self.project_name
        data["ENVIRONMENT"] = self.project_env
        if (self.project_env.upper() in self.PARAMS.keys()):
            data[self.project_env.upper()] = self.PARAMS[self.project_env.upper()]
        data["S_RUN_ID"] = self.s_run_id
        # data["USER"] = self.user
        data["MACHINE"] = self.machine
        data["REPORT_LOCATION"] = self.testcase_folder
        data["SUITE_VARS"] = self.user_suite_variables
        data["INVOKE_USER"] = self.invoke_user
        data["USER"] = self.user
        data['GLOBAL_VARIABLES'] = self.user_global_variables
        updated_config_data = self.replace_vars_in_testcase(
            data["config_data"], self.user_global_variables)
        data["config_data"] = updated_config_data
        return data

    def getDependency(self, testcases: Dict):
        """
        yields the testcases with least dependncy first
        Reverse toplogical sort
        accept all testcases dictionary as arguments
        """
        adj_list = {}
        for key, value in testcases.items():

            adj_list[key] = list(
                set(list(value.get("DEPENDENCY", "").upper().split(","))) - set([""]))

        for key, value in adj_list.items():
            new_list = []
            for testcase in value:

                testcase = testcase.split(":")
                if len(testcase) > 1:
                    new_list.append(testcase[1])
                else:
                    new_list.append(testcase[0])

            adj_list[key] = set(new_list)

        while adj_list:
            """
            return testcases that doesn't depend on other testcase
            """
            top_dep = set(
                i for dependents in list(adj_list.values()) for i in dependents
            ) - set(adj_list.keys())
            top_dep.update(key for key, value in adj_list.items() if not value)

            if not top_dep:
                logging.critical(
                    "circular dependency found please remove the cirular dependency"
                )
                logging.debug("possible testcase with circular dependencies")
                sys.exit(1)

            adj_list = {key: value - top_dep for key,
                        value in adj_list.items() if value}
            result = []
            for key in testcases:
                if key in top_dep:
                    result.append(testcases[key])
            yield result

    def isDependencyPassed(self, testcase: Dict) -> bool:
        """
        cheks if the dependency is passed for the testcase or not
        """

        # split on ','
        listOfTestcases = []
        # post 1.0.4
        listOfTestcases = list(set(list(testcase.get("DEPENDENCY", "").upper().split(
            ","))) - set([""]))  # if testcase.get("DEPENDENCY", None) else listOfTestcases
        for dep in listOfTestcases:

            dep_split = list(dep.split(":"))
            if len(dep_split) == 1:
                # NAME to name, to_list()
                if dep_split[0] not in self.DATA.testcase_details["name"].to_list():
                    return 'err'

            else:
                if dep_split[0].upper() == "P":
                    if dep_split[1] not in self.DATA.testcase_details["name"].to_list():
                        return 'err'
                    # way to parsing the df
                    if ((self.DATA.testcase_details[self.DATA.testcase_details["name"] == dep_split[1]]['status'].iloc[0]) != status.PASS.name):
                        return 'fail'

                if dep_split[0].upper() == "F":
                    if dep_split[1] not in self.DATA.testcase_details["name"].to_list():
                        return 'err'
                    if (
                        (self.DATA.testcase_details[self.DATA.testcase_details["name"]
                        == dep_split[1]]['status'].iloc[0])
                        != status.FAIL.name
                    ):
                        return 'fail'

        return 'true'

    # Function for sending total, pass, fail in order
    def totalOrder(self, unsorted_dict):

        prio_list = ['TOTAL', 'PASS', 'FAIL']
        sorted_dict = {}
        for key in prio_list:
            if key in unsorted_dict:
                sorted_dict[key] = unsorted_dict[key]
                unsorted_dict.pop(key)
            elif key == "PASS" or key == 'FAIL':
                sorted_dict[key] = 0
        sorted_dict.update(unsorted_dict)
        return sorted_dict

    def sortTestcase(self, all_config_data: Type[Dict]):
        priority_list = list()
        unpriority_list = list()
        global_vars = list()
        sorted_testcase_dict = dict()
        suite_data = all_config_data["SUITE_DATA"]
        testcase_data = all_config_data["TESTCASE_DATA"]
        for testcase, each_testcase_data in testcase_data.items():
            if (each_testcase_data.get("GLOBAL_VARS", None) is not None):
                priority_list.append(testcase)
                vars = each_testcase_data["GLOBAL_VARS"]
                vars_list = vars.split(";")
                for v in vars_list:
                    global_vars.append(v)
            else:
                unpriority_list.append(testcase)
        global_variables_dict = self.fetchGlobalVariableDetails(global_vars)
        updated_testcase_data = self.update_testcase_values(
            testcase_data, global_variables_dict)
        for testcase in priority_list:
            if ("GLOBAL_VARS" in updated_testcase_data.get(testcase).keys()):
                sorted_testcase_dict[testcase] = updated_testcase_data[testcase]
            else:
                unpriority_list.append(testcase)
        for testcase in unpriority_list:
            sorted_testcase_dict[testcase] = updated_testcase_data[testcase]
        suite_data["GLOBAL_VARIABLES"] = global_variables_dict
        all_config_data["TESTCASE_DATA"] = sorted_testcase_dict
        return all_config_data

    def fetchGlobalVariableDetails(self, global_vars: type[list]):
        self.update_global_value = list()
        filtered_global_var = dict()
        for var in global_vars:
            if "SET" in var.upper() and '$[#' in var:
                variable_name = (var.split("=")[0]).replace(".", "_").replace(
                    "set".casefold(), "").replace("$[#", "").replace("]", "").replace(" ", "")
                value = var.split("=")[1]
                filtered_global_var[variable_name.upper()] = value
                if '$[#' in value:
                    self.update_global_value.append(variable_name)
        return filtered_global_var

    def update_testcase_values(self, testcase_data, global_variables_dict):
        # optimize testcase data, if global variable has constant data then it is global_vars tag is removed from testcase
        for _, testcase_val in testcase_data.items():
            condition = list()
            flag = False
            for param, value in testcase_val.items():
                if param.casefold() == "GLOBAL_VARS".casefold():
                    flag = True
                    global_var_list = value.split(";")
                    for global_vars in global_var_list:
                        if "$[#" in global_vars.split("=")[1].strip(" "):
                            condition.append(global_vars)

                if "$[#GLOBAL." in value.replace(" ", "") and "SET$[#GLOBAL.".casefold() not in value.replace(" ", ""):
                    # global_var = value.replace("$[#", "").replace(" ", "").replace(".", "_").replace("]", "")
                    var_name = (value[value.find("$"): value.find("]")]).replace(
                        "$[#", "").replace("]", "").replace(".", "_")
                    var_value = global_variables_dict.get(var_name.upper())
                    if var_value is None or "$[#" in var_value:
                        continue
                    final_param_value = value[:value.find(
                        "$")] + var_value + value[value.find("]") + 1:]
                    testcase_val[param] = final_param_value
            if flag == True and len(condition) == 0:
                del testcase_val["GLOBAL_VARS"]
                flag = False
            elif flag == True:
                condition_str = ";".join(condition)
                testcase_val["GLOBAL_VARS"] = condition_str

        return testcase_data

    def replace_vars_in_testcase(self, testcase_config_data, global_variables):
        for key, val in testcase_config_data.items():
            if type(val) is str and val is not None and "SET$[#GLOBAL.".casefold() not in val.replace(" ", "").casefold() and "$[#GLOBAL.".casefold() in val.strip(" ").casefold():
                if val.find("$") != -1 and val.find("[") != -1:
                    temp_var = val[val.find("$"): val.find("]")]
                    global_var_name = temp_var.replace(" ", "").replace(
                        "$[#", "").replace("]", "").replace(".", "_")
                    # and "$[#" not in global_variables.get(global_var_name.upper())
                    if global_variables.get(global_var_name.upper(), None) is not None:
                        new_val_to_key = val[:val.find(
                            "$")] + str(global_variables.get(global_var_name.upper())) + val[val.find("]") + 1:]
                        testcase_config_data[key] = new_val_to_key
        return testcase_config_data            
                        
