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
# from tomlkit import date
from gempyp.config.baseConfig import abstarctBaseConfig
from gempyp.engine.testData import testData
from gempyp.libs.enums.status import status
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

    print("-------------- In Executor Factory --------------------\n")
    # print("!!!!!!!!!!!!!!", data["configData"]["TYPE"])

    if not custom_logger:
        # log_path = os.path.join(os.environ.get('log_dir'),data['configData'].get('NAME') + '_'
        log_path = os.path.join(os.environ.get('TESTCASE_LOG_FOLDER'),data['configData'].get('NAME') + '_'
        + os.environ.get('unique_id') + '.log')
        custom_logger = my_custom_logger(log_path)
    data['configData']['LOGGER'] = custom_logger
    if 'log_path' not in data['configData']:
        data['configData']['LOG_PATH'] = log_path


    if "TYPE" not in data["configData"] or data["configData"].get("TYPE").upper() == "GEMPYP":
        custom_logger.info("starting the GemPyP testcase")
        #custom_logger.setLevel(logging.INFO)
        return testcaseRunner(data)

    elif data["configData"].get("TYPE").upper() == "DVM":
        # TODO do the DVM stuff
        logging.info("starting the DVM testcase")
    elif data["configData"].get("TYPE").upper() == "PYPREST":
        # TODO do the resttest stuff here
        custom_logger.info("starting the PYPREST testcase")
        try:
            return PypRest(data).restEngine()
        except Exception as e:
            traceback.print_exc()
            print(e)
            return None, getError(e, data["configData"])


class Engine:
    def __init__(self, params_config):
        """
        constructor used to  call run method
        """
        # logging.basicConfig()
        # logging.root.setLevel(logging.DEBUG)
        self.run(params_config)

    def run(self, params_config: Type[abstarctBaseConfig]):
        """
        main method to call other methods that are required for report generation
        """
        logging.info("Engine Started")
        # initialize the data class
        

        self.DATA = testData()
        # get the env for the engine Runner
        self.ENV = os.getenv("ENV_BASE", "BETA").upper()
        # initial SETUP
        self.setUP(params_config)
        self.parseMails()
        self.makeSuiteDetails()
        dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])
        self.makeOutputFolder()
        self.start()
        self.updateSuiteData()
        dataUpload.sendSuiteData(self.DATA.toSuiteJson(), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"], mode="PUT")
        self.makeReport()

    def makeOutputFolder(self):
        """
        to make GemPyp_Report folder 
        """

        logging.info("---------- Making output folders -------------")
        report_folder_name = f"{self.projectName}_{self.project_env}"
        if self.reportName:
            report_folder_name = report_folder_name + f"_{self.reportName}"
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


    def setUP(self, config: Type[abstarctBaseConfig]):
        """
        assigning values to some attributes which will be used in method makeSuiteDetails
        """
        # method_list = inspect.getmembers(MyClass, predicate=inspect.ismethod)
        self.PARAMS = config.getSuiteConfig()
        self.CONFIG = config
        self.testcaseData = {}
        self.machine = platform.node()
        if("USERNAME" in self.PARAMS):
            self.user = self.PARAMS["USERNAME"]
        else:
            self.user=getpass.getuser()
        self.current_dir = os.getcwd()
        self.platform = platform.system()
        self.start_time = datetime.now(timezone.utc)
        self.projectName = self.PARAMS["PROJECT"]
        self.reportName = self.PARAMS.get("REPORT_NAME")
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
        self.s_run_id = f"{self.projectName}_{self.project_env}_{self.unique_id}"
        self.s_run_id = self.s_run_id.upper()
        logging.info("S_RUN_ID: {}".format(self.s_run_id))
        run_mode = "LINUX_CLI"
        if os.name == 'nt':
            run_mode = "WINDOWS"
        SuiteDetails = {
            "s_run_id": self.s_run_id,
            "s_start_time": self.start_time,
            "s_end_time": None,
            "status": status.EXE.name,
            "project_name": self.projectName,
            "run_type": "ON DEMAND",
            "report_type": self.reportName,
            "user": self.user,
            "env": self.project_env,
            "machine": self.machine,
            "initiated_by": self.user,
            "run_mode": run_mode,
        }
        self.DATA.suiteDetail = self.DATA.suiteDetail.append(
            SuiteDetails, ignore_index=True
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
        statusDict = self.DATA.testcaseDetails["status"].value_counts().to_dict()
        SuiteStatus = status.FAIL.name

        # based on the status priority
        for s in status:
            if statusDict.get(s.name, 0) > 0:
                SuiteStatus = s.name

        stoptime = (
            self.DATA.testcaseDetails["end_time"].sort_values(ascending=False).iloc[0]
        )
        self.DATA.suiteDetail.at[0, "status"] = SuiteStatus
        self.DATA.suiteDetail.at[0, "s_end_time"] = stoptime

    def startSequence(self):
        """
        start running the testcases in sequence
        """

        for testcases in self.getDependency(self.CONFIG.getTestcaseConfig()):
            for testcase in testcases:
                data = self.getTestcaseData(testcase['NAME'])
                # log_path = os.path.join(self.CONFIG.getSuiteConfig()['LOG_DIR'],
                log_path = os.path.join(self.testcase_log_folder,
                data['configData'].get('NAME')+'_'+self.CONFIG.getSuiteConfig()['UNIQUE_ID'] + '.log')
                custom_logger = my_custom_logger(log_path)
                data['configData']['log_path'] = log_path
                #LoggingConfig(data['configData'].get('NAME')+'.log')
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
                poolList = []
                for testcase in testcases:
                    #custom_logger = my_custom_logger(testcase.get("NAME")+'.log')
                    # only append testcases whose dependency are passed otherwise just update the database
                    if self.isDependencyPassed(testcase):
                        poolList.append(self.getTestcaseData(testcase.get("NAME")))
                    else:
                        print("----------------here--------------------")
                        dependencyError = {
                            "message": "dependency failed",
                            "testcase": testcase["NAME"],
                            "category": testcase.get("CATEGORY", None),
                            "product_type": testcase.get("PRODUCT_TYPE", None),
                        }
                        ####### handle dependency error in jsondata(update_df)

                        # update the testcase in the database with failed dependency
                        self.update_df(None, dependencyError)

                if len(poolList) == 0:
                    continue
                # runs the testcase in parallel here
                results = pool.map(executorFactory, poolList)
                # sys.exit()  
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

                i["testcaseDict"]["steps"] = i["jsonData"]["steps"]
                
                testcaseDict = i["testcaseDict"]
                try:
                    """ update suite vars here from testcaseDict["suite_variables"] append it in the suite vars of _config"""
    
                    self.user_suite_variables.update(i.get("suite_variables", {}))
                    
                    self.testcaseData[testcaseDict.get("tc_run_id")] = i["jsonData"]
                except Exception as e:
                    logging.error(e)

                self.DATA.testcaseDetails = self.DATA.testcaseDetails.append(
                    testcaseDict, ignore_index=True
                )
                self.updateTestcaseMiscData(
                    i["misc"], tc_run_id=testcaseDict.get("tc_run_id")
                )
                dataUpload.sendTestcaseData((self.DATA.totestcaseJson(testcaseDict.get("tc_run_id").upper(), self.s_run_id)), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])

        except Exception as e:
            logging.error("in update_df: {e}".format(e=e))

    def getErrorTestcase(
        self,
        message: str,
        testcaseName: str,
        category: str = None,
        product_type: str = None,
        log_path: str = None
    ) -> Dict:
        """
        store the data of failed testcase and return it as a dict
        """

        result = {}
        testcaseDict = {}
        misc = {}
        if not self.unique_id:
            self.unique_id = uuid.uuid4()
        tc_run_id = f"{testcaseName}_{self.project_env}_{self.unique_id}"
        tc_run_id = tc_run_id.upper()
        testcaseDict["tc_run_id"] = tc_run_id
        testcaseDict["status"] = status.FAIL.name
        testcaseDict["start_time"] = datetime.now(timezone.utc)
        testcaseDict["end_time"] = datetime.now(timezone.utc)
        testcaseDict["name"] = testcaseName
        testcaseDict["ignore"] = False
        if category:
            testcaseDict["category"] = category
        testcaseDict["log_file"] = log_path
        testcaseDict["result_file"] = None
        testcaseDict["user"] = self.user
        testcaseDict["machine"] = self.machine
        if product_type:
            testcaseDict["product_type"] = product_type

        result["testcaseDict"] = testcaseDict

        misc["REASON_OF_FAILURE"] = message

        result["misc"] = misc

        return result

    def updateTestcaseMiscData(self, misc: Dict, tc_run_id: str):
        """
        updates the misc data for the testcases
        """
        miscList = []

        for miscData in misc:
            temp = {}
            # storing all the key in upper so that no duplicate data is stored
            temp["key"] = miscData.upper()
            temp["value"] = misc[miscData]
            temp["run_id"] = tc_run_id
            temp["table_type"] = "TESTCASE"
            miscList.append(temp)

        self.DATA.miscDetails = self.DATA.miscDetails.append(
            miscList, ignore_index=True
        )

    def getTestcaseData(self, testcase: str) -> Dict:
        """
        taking argument as the testcase name and  return
        """
        data = {}
        data["configData"] = self.CONFIG.getTestcaseData(testcase)
        data["PROJECTNAME"] = self.projectName
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

        adjList = {
            key: list(set(list(value.get("DEPENDENCY", "").split(","))) - set([""])) for key, value in testcases.items()
        }

        for key, value in adjList.items():
            new_list = []
            for testcase in value:
                testcase = testcase.split(":")
                if len(testcase) > 1:
                    new_list.append(testcase[1])
                else:
                    new_list.append(testcase[0])

            adjList[key] = set(new_list)
        while adjList:
            top_dep = set(
                i for dependents in list(adjList.values()) for i in dependents
            ) - set(adjList.keys())
            top_dep.update(key for key, value in adjList.items() if not value)

            if not top_dep:
                logging.critical(
                    "circular dependency found please remove the cirular dependency"
                )
                logging.debug("possible testcase with circular dependencies")
                # logging.error(adjList.keys())
                sys.exit(1)

            adjList = {key: value - top_dep for key, value in adjList.items() if value}

            result = []
            for key in testcases:
                if key in top_dep:
                    result.append(testcases[key])
            yield result

    def isDependencyPassed(self, testcase: Dict) -> bool:
        """
        cheks if the dependency is passed for the testcase or not
        """

        ###### split on ','
        for dep in list(set(list(testcase.get("DEPENDENCY", "").split(","))) - set([""])):

            dep_split = list(dep.split(":"))

            if len(dep_split) == 1:
                ####### NAME to name, to_list()
                if dep_split[0] not in self.DATA.testcaseDetails["name"].to_list():
                    return False

            else:
                if dep_split[0].upper() == "P":
                    if dep_split[1] not in self.DATA.testcaseDetails["name"].to_list():
                        return False
                    ####### way to parsing the df    
                    if ((self.DATA.testcaseDetails[self.DATA.testcaseDetails["name"] == dep_split[1]]['status'].iloc[0]) != status.PASS.name):
                        return False

                if dep_split[0].upper() == "F":
                    if dep_split[1] not in self.DATA.testcaseDetails["name"].to_list():
                        return False
                    if (
                        (self.DATA.testcaseDetails[self.DATA.testcaseDetails["name"] == dep_split[1]]['status'].iloc[0])
                        != status.FAIL.name
                    ):
                        return False

        return True

    def makeReport(self):
        """
        saves the report json 
        """
        suiteReport = None

        self.date = datetime.now().strftime("%Y_%b_%d_%H%M%S_%f")

        suite_path = os.path.dirname(__file__)
        suite_path = os.path.join(os.path.split(suite_path)[0], "final_report.html")
        with open(suite_path, "r") as f:
            suiteReport = f.read()

        reportJson = self.DATA.getJSONData()
        reportJson = json.loads(reportJson)
        reportJson["TestStep_Details"] = self.testcaseData
        self.repJson = reportJson
        # self.testcaseData = json.dumps(self.testcaseData)
        reportJson = json.dumps(reportJson)
        suiteReport = suiteReport.replace("DATA", reportJson)

        ResultFile = os.path.join(self.ouput_folder, "Result_{}.html".format(self.date))
        self.ouput_file_path = ResultFile
        with open(ResultFile, "w+") as f:
            f.write(suiteReport)
        self.repSummary()
    
    def repSummary(self):
        """
        logging some information
        """
        try:
            logging.info("---------- Finalised the report --------------")
            logging.info("============== Run Summary =============")
            count_info = {key.lower(): val for key, val in self.repJson['Suits_Details']['Testcase_Info'].items()}
            log_str = f"Total Testcases: {str(count_info.get('total', 0))} | Passed Testcases: {str(count_info.get('pass', 0))} | Failed Testcases: {str(count_info.get('fail', 0))} | "
            status_dict = {"info": "Info", "warn": "WARN", "exe": "Exe"}
            for key, val in count_info.items():
                if key in status_dict.keys():
                    log_str += f"{status_dict[key.lower()]} Testcases: {val} | "
        

            logging.info(log_str.strip(" | "))
            
            logging.info('-------- Report created Successfully at: {path}'.format(path=self.ouput_file_path))


        except Exception as e:
            logging.error(traceback.print_exc(e))
