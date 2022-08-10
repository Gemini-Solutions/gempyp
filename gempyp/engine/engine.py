from pathlib import Path
import sys
import os
import platform
import getpass
import json
import traceback
from multiprocessing import Pool
from typing import Dict, List, Tuple, Type
import uuid
from datetime import datetime, timezone
from gempyp.config.baseConfig import AbstarctBaseConfig
from gempyp.engine.testData import TestData
from gempyp.libs.enums.status import status
from gempyp.reporter.reportGenerator import TemplateData
from gempyp.libs import common
from gempyp.engine.runner import testcaseRunner, getError
from gempyp.config import DefaultSettings
import logging
from gempyp.libs.logConfig import my_custom_logger
from gempyp.engine import dataUpload
from gempyp.pyprest.pypRest import PypRest


def executorFactory(data: Dict, custom_logger=None) -> Tuple[List, Dict]:
    
    """
    calls the differnt executors based on the type of the data
    """

    print("--------- In Executor Factory ----------\n")


    if not custom_logger:
        log_path = os.path.join(os.environ.get('TESTCASE_LOG_FOLDER'),data['config_data'].get('NAME') + '_'
        + os.environ.get('unique_id') + '.log')
        custom_logger = my_custom_logger(log_path)
    data['config_data']['LOGGER'] = custom_logger
    if 'log_path' not in data['config_data']:
        data['config_data']['LOG_PATH'] = log_path


    if "TYPE" not in data["config_data"] or data["config_data"].get("TYPE").upper() == "GEMPYP":
        custom_logger.info("starting the GemPyP testcase")
        #custom_logger.setLevel(logging.INFO)
        return testcaseRunner(data)

    elif data["config_data"].get("TYPE").upper() == "DVM":
        # TODO do the DVM stuff
        logging.info("starting the DVM testcase")
    elif data["config_data"].get("TYPE").upper() == "PYPREST":
        # TODO do the resttest stuff here
        custom_logger.info("starting the PYPREST testcase")
        try:
            return PypRest(data).restEngine()
        except Exception as e:
            traceback.print_exc()
            print(e)
            return None, getError(e, data["config_data"])


class Engine:
    def __init__(self, params_config):
        """
        constructor used to  call run method
        """
        # logging.basicConfig()
        # logging.root.setLevel(logging.DEBUG)
        self.run(params_config)

    def run(self, params_config: Type[AbstarctBaseConfig]):
        """
        main method to call other methods that are required for report generation
        """
        logging.info("Engine Started")
        # initialize the data class
        

        self.DATA = TestData()
        # get the env for the engine Runner
        self.ENV = os.getenv("ENV_BASE", "BETA").upper()
        # initial SETUP
        self.setUP(params_config)
        self.parseMails()
        self.makeSuiteDetails()
        if("USERNAME" in self.PARAMS.keys() and "BRIDGE_TOKEN" in self.PARAMS.keys()):
            dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])
        else:
            logging.warning("Either username or bridgetoken is missing thus data is not uploaded in db.")
        self.makeOutputFolder()
        self.start()
        self.updateSuiteData()
        if("USERNAME" in self.PARAMS.keys() and "BRIDGE_TOKEN" in self.PARAMS.keys()):
            dataUpload.sendSuiteData(self.DATA.toSuiteJson(), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"], mode="PUT")
        self.repJson, output_file_path = TemplateData().makeSuiteReport(self.DATA.getjson_data(), self.testcaseData, self.ouput_folder)
        TemplateData().repSummary(self.repJson, output_file_path)

    def makeOutputFolder(self):
        """
        to make GemPyp_Report folder 
        """

        logging.info("---------- Making output folders -------------")
        report_folder_name = f"{self.project_name}_{self.project_env}"
        if self.report_name:
            report_folder_name = report_folder_name + f"_{self.report_name}"
        date = datetime.now().strftime("%Y_%b_%d_%H%M%S_%f")
        report_folder_name = report_folder_name + f"_{date}"
        if "OUTPUT_FOLDER" in self.PARAMS and self.PARAMS["OUTPUT_FOLDER"]:
            self.ouput_folder = os.path.join(
                self.PARAMS["OUTPUT_FOLDER"], report_folder_name
            )
        else:
            home = str(Path.home())
            self.ouput_folder = os.path.join(
                home, "gempyp_reports", report_folder_name
            )

        os.makedirs(self.ouput_folder)
        self.testcase_folder = os.path.join(self.ouput_folder, "testcases")
        os.makedirs(self.testcase_folder)
        self.testcase_log_folder = os.path.join(self.ouput_folder, "logs")
        os.environ['TESTCASE_LOG_FOLDER'] = self.testcase_log_folder
        os.makedirs(self.testcase_log_folder)

    def setUP(self, config: Type[AbstarctBaseConfig]):
        """
        assigning values to some attributes which will be used in method makeSuiteDetails
        """
        self.PARAMS = config.getSuiteConfig()
        self.CONFIG = config
        self.testcase_data = {}
        self.machine = platform.node()
        if("USERNAME" in self.PARAMS):
            self.user = self.PARAMS["USERNAME"]
        else:
            self.user=getpass.getuser()
        self.current_dir = os.getcwd()
        self.platform = platform.system()
        self.start_time = datetime.now(timezone.utc)
        self.project_name = self.PARAMS["PROJECT"]
        self.report_name = self.PARAMS.get("REPORT_NAME")
        self.project_env = self.PARAMS["ENV"]
        self.unique_id = self.PARAMS["UNIQUE_ID"]
        self.user_suite_variables = self.PARAMS["SUITE_VARS"]
        

        #add suite_vars here 

    def parseMails(self):
        """
        to get the mail from the configData
        """
        self.mail = common.parseMails(self.PARAMS["MAIL"])
        print(self.mail)

    def makeSuiteDetails(self):
        """
        making suite Details 
        """
        if not self.unique_id:
            self.unique_id = uuid.uuid4()
        self.s_run_id = f"{self.project_name}_{self.project_env}_{self.unique_id}"
        self.s_run_id = self.s_run_id.upper()
        logging.info("S_RUN_ID: {}".format(self.s_run_id))
        run_mode = "LINUX_CLI"
        if os.name == 'nt':
            run_mode = "WINDOWS"
        suite_details = {
            "s_run_id": self.s_run_id,
            "s_start_time": self.start_time,
            "s_end_time": None,
            "status": status.EXE.name,
            "project_name": self.project_name,
            "run_type": "ON DEMAND",
            "report_type": self.report_name,
            "user": self.user,
            "env": self.project_env,
            "machine": self.machine,
            "initiated_by": self.user,
            "run_mode": run_mode,
        }
        self.DATA.suite_detail = self.DATA.suite_detail.append(
            suite_details, ignore_index=True
        )

    def start(self):

        """
         check the mode and start the testcases accordingly
        """

        try:
            if self.CONFIG.getTestcaseLength() <= 0:
                raise Exception("no testcase found to run")

            if self.PARAMS["MODE"].upper() == "SEQUENCE":
                self.startSequence()
            elif self.PARAMS["MODE"].upper() == "OPTIMIZE" or self.PARAMS.get("MODE", None) is None:
                self.startParallel()
            else:
                raise TypeError("mode can only be sequence or optimize")

        except Exception:
            logging.error(traceback.format_exc())
            pass

    def updateSuiteData(self):
        """
        updates the suiteData after all the runs have been executed
        """

        # get the status count of the status
        status_dict = self.DATA.testcase_details["status"].value_counts().to_dict()
        Suite_status = status.FAIL.name

        # based on the status priority
        for s in status:
            if status_dict.get(s.name, 0) > 0:
                Suite_status = s.name
                break
        stop_time = (
            self.DATA.testcase_details["end_time"].sort_values(ascending=False).iloc[0]
        )
        self.DATA.suite_detail.at[0, "status"] = Suite_status
        self.DATA.suite_detail.at[0, "s_end_time"] = stop_time

    def startSequence(self):
        """
        start running the testcases in sequence
        """
        for testcases in self.getDependency(self.CONFIG.getTestcaseConfig()):
            for testcase in testcases:
                data = self.getTestcaseData(testcase['NAME'])
                log_path = os.path.join(self.testcase_log_folder,
                data['config_data'].get('NAME')+'_'+self.CONFIG.getSuiteConfig()['UNIQUE_ID'] + '.log')
                custom_logger = my_custom_logger(log_path)
                data['config_data']['log_path'] = log_path
                output, error = executorFactory(data, custom_logger)
                
                if error:
                    custom_logger.error(
                        f"Error occured while executing the testcase: {error['testcase']}"
                    )
                    custom_logger.error(f"message: {error['message']}")
                self.update_df(output, error)


    def startParallel(self):
        """
        start running the testcases in parallel
        """
        pool = None
        try:
            threads = self.PARAMS.get("THREADS", DefaultSettings.THREADS)
            try:
                threads = int(threads)
            except:
                threads = DefaultSettings.THREADS
            pool = Pool(threads)
            # decide the dependency order:
            for testcases in self.getDependency(self.CONFIG.getTestcaseConfig()):
                if len(testcases) == 0:
                    raise Exception("No testcase to run")
                pool_list = []
                for testcase in testcases:
                    # only append testcases whose dependency are passed otherwise just update the database
                    if self.isDependencyPassed(testcase):
                        pool_list.append(self.getTestcaseData(testcase.get("NAME")))
                    else:
                        print("----------------here--------------------")
                        dependency_error = {
                            "message": "dependency failed",
                            "testcase": testcase["NAME"],
                            "category": testcase.get("CATEGORY", None),
                            "product_type": testcase.get("PRODUCT_TYPE", None),
                        }
                        # handle dependency error in json_data(update_df)
                        # update the testcase in the database with failed dependency
                        self.update_df(None, dependency_error)

                if len(pool_list) == 0:
                    continue
                # runs the testcase in parallel here
                results = pool.map(executorFactory, pool_list)
                for row in results:
                    if not row or len(row) < 2:
                        raise Exception(
                            "Some error occured while running the testcases"
                        )
                    output = row[0]
                    error = row[1]
                    if error:
                        logging.error(
                            f"Error occured while executing the testcase: {error['testcase']}"
                        )
                        logging.error(f"message: {error['message']}")
                    self.update_df(output, error)
        except Exception:
            logging.error(traceback.format_exc())

        finally:
            if pool:
                pool.close()

    def update_df(self, output: List, error: Dict):

        """
        updates the testcase data in the dataframes
        like
        """
        try:
            if error:
                output = self.getErrorTestcase(
                    error["message"],
                    error["testcase"],
                    error.get("category"),
                    error.get("product_type"),
                    error.get('log_path', None)
                )
                output = [output]
            for i in output:

                i["testcase_dict"]["steps"] = i["json_data"]["steps"]
                
                testcase_dict = i["testcase_dict"]
                try:
                    """ update suite vars here from testcase_dict["suite_variables"] append it in the suite vars of _config"""
    
                    self.user_suite_variables.update(i.get("suite_variables", {}))
                    
                    self.testcase_data[testcase_dict.get("tc_run_id")] = i["json_data"]
                except Exception as e:
                    logging.error(e)

                self.DATA.testcase_details = self.DATA.testcase_details.append(
                    testcase_dict, ignore_index=True
                )
                self.updateTestcaseMiscData(
                    i["misc"], tc_run_id=testcase_dict.get("tc_run_id")
                )
                if("USERNAME" in self.PARAMS.keys() and "BRIDGE_TOKEN" in self.PARAMS.keys()):
                    dataUpload.sendTestcaseData((self.DATA.totestcaseJson(testcase_dict.get("tc_run_id").upper(), self.s_run_id)), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])
        except Exception as e:
            logging.error("in update_df: {e}".format(e=e))

    def getErrorTestcase(
        self,
        message: str,
        testcase_name: str,
        category: str = None,
        product_type: str = None,
        log_path: str = None
    ) -> Dict:
        """
        store the data of failed testcase and return it as a dict
        """

        result = {}
        testcase_dict = {}
        misc = {}
        if not self.unique_id:
            self.unique_id = uuid.uuid4()
        tc_run_id = f"{testcase_name}_{self.project_env}_{self.unique_id}"
        tc_run_id = tc_run_id.upper()
        testcase_dict["tc_run_id"] = tc_run_id
        testcase_dict["status"] = status.FAIL.name
        testcase_dict["start_time"] = datetime.now(timezone.utc)
        testcase_dict["end_time"] = datetime.now(timezone.utc)
        testcase_dict["name"] = testcase_name
        testcase_dict["ignore"] = False
        if category:
            testcase_dict["category"] = category
        testcase_dict["log_file"] = log_path
        testcase_dict["result_file"] = None
        testcase_dict["user"] = self.user
        testcase_dict["machine"] = self.machine
        if product_type:
            testcase_dict["product_type"] = product_type

        result["testcase_dict"] = testcase_dict

        misc["REASON_OF_FAILURE"] = message

        result["misc"] = misc

        return result

    def updateTestcaseMiscData(self, misc: Dict, tc_run_id: str):
        """
        updates the misc data for the testcases
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
        taking argument as the testcase name and  return
        """
        data = {}
        data["config_data"] = self.CONFIG.getTestcaseData(testcase)
        data["PROJECT_NAME"] = self.project_name
        data["ENV"] = self.project_env
        data["S_RUN_ID"] = self.s_run_id
        data["USER"] = self.user
        data["MACHINE"] = self.machine
        data["OUTPUT_FOLDER"] = self.testcase_folder
        data["SUITE_VARS"] = self.user_suite_variables
        return data

    def getDependency(self, testcases: Dict):
        """
        yields the testcases with least dependncy first
        Reverse toplogical sort
        """

        adj_list = {
            key: list(set(list(value.get("DEPENDENCY", "").split(","))) - set([""])) for key, value in testcases.items()
        }

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

            adj_list = {key: value - top_dep for key, value in adj_list.items() if value}

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
        for dep in list(set(list(testcase.get("DEPENDENCY", "").split(","))) - set([""])):

            dep_split = list(dep.split(":"))

            if len(dep_split) == 1:
                # NAME to name, to_list()
                if dep_split[0] not in self.DATA.testcase_details["name"].to_list():
                    return False

            else:
                if dep_split[0].upper() == "P":
                    if dep_split[1] not in self.DATA.testcase_details["name"].to_list():
                        return False
                    # way to parsing the df    
                    if ((self.DATA.testcase_details[self.DATA.testcase_details["name"] == dep_split[1]]['status'].iloc[0]) != status.PASS.name):
                        return False

                if dep_split[0].upper() == "F":
                    if dep_split[1] not in self.DATA.testcase_details["name"].to_list():
                        return False
                    if (
                        (self.DATA.testcase_details[self.DATA.testcase_details["name"] == dep_split[1]]['status'].iloc[0])
                        != status.FAIL.name
                    ):
                        return False

        return True
