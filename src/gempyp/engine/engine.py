import sys
import os
import logging
import platform
import getpass
import json
import traceback
from multiprocessing import Pool
from typing import Dict, List, Tuple, Type
import uuid
from datetime import datetime, timezone
from gempyp.config.baseConfig import abstarctBaseConfig
from gempyp.engine.testData import testData
from gempyp.libs.enums.status import status
from gempyp.libs import common
from gempyp.engine.runner import testcaseRunner, getError
from gempyp.config import DefaultSettings
from gempyp.engine import dataUpload


def executorFactory(data: Dict) -> Tuple[List, Dict]:
    """
    calls the differnt executors based on the type of the data
    """

    if "TYPE" not in data["configData"]:
        logging.info("starting the GemPyP testcases")
        return testcaseRunner(data)

    elif data["configData"].get("TYPE").upper() == "DVM":
        # TODO do the DVM stuff
        logging.info("starting the DVM testcase")
    elif data["configData"].get("TYPE").upper() == "PYPREST":
        # TODO do the resttest stuff here
        logging.info("starting the resttest testcase")
        # try:
        #     return PIREST(data).rest_engine()
        # except Exception as e:
        #     print(traceback.print_exc())
        #     print(e)
        #     return None, getError(e, data["configData"])


class Engine:
    def __init__(self, params_config):
        logging.basicConfig()
        logging.root.setLevel(logging.DEBUG)
        self.run(params_config)

    def run(self, params_config: Type[abstarctBaseConfig]):
        logging.info("Engine Started")
        # initialize the data class
        self.DATA = testData()
        # get the env for the engine Runner
        self.ENV = os.getenv("ENV_BASE", "BETA").upper()
        # initial SETUP
        self.setUP(params_config)
        self.parseMails()
        self.makeSuiteDetails()
        dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.PARAMS["BRIDGE_TOKEN"])
        self.makeOutputFolder()
        self.start()
        self.updateSuiteData()
        dataUpload.sendSuiteData(self.DATA.toSuiteJson(), self.PARAMS["BRIDGE_TOKEN"], mode="PUT")
        self.makeReport()

    def makeOutputFolder(self):

        report_folder_name = f"{self.projectName}_{self.project_env}"
        if self.reportName:
            report_folder_name = report_folder_name + f"_{self.reportName}"
        date = datetime.now().strftime("%Y_%b_%d_%H%M%S_%f")
        report_folder_name = report_folder_name + f"_{date}"
        if "outputfolder" in self.PARAMS:
            self.ouput_folder = os.path.join(
                self.PARAMS["OUTPUTFOLDER"], report_folder_name
            )
        else:
            self.ouput_folder = os.path.join(
                self.current_dir, "gempyp_reports", report_folder_name
            )

        os.makedirs(self.ouput_folder)
        self.testcase_folder = os.path.join(self.ouput_folder, "testcases")
        os.makedirs(self.testcase_folder)

    def setUP(self, config: Type[abstarctBaseConfig]):
        self.PARAMS = config.getSuiteConfig()
        self.CONFIG = config
        self.testcaseData = {}
        self.machine = platform.node()
        self.user = getpass.getuser()
        self.current_dir = os.getcwd()
        self.platform = platform.system()
        self.start_time = datetime.now(timezone.utc)
        self.projectName = self.PARAMS["PROJECT"]
        self.reportName = self.PARAMS.get("REPORT_NAME")
        # print("---------- report Name", self.reportName)
        self.project_env = self.PARAMS["ENV"]

    def parseMails(self):
        self.mail = common.parseMails(self.PARAMS["MAIL"])

    def makeSuiteDetails(self):

        self.s_run_id = f"{self.projectName}_{self.project_env}_{uuid.uuid4()}"
        self.s_run_id = self.s_run_id.upper()
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

        # check the mode and start the testcases accordingly

        try:
            if self.CONFIG.getTestcaseLength() <= 0:
                raise Exception("no testcase found to run")

            if self.PARAMS["MODE"].upper() == "SEQUENCE":
                self.startSequence()
            elif self.PARAMS["MODE"].upper() == "OPTIMIZE":
                self.startParallel()
            else:
                raise TypeError("mode can only be sequence of optimize")

        except Exception as e:
            common.errorHandler(
                logging, e, "Some Error occured while running the testcases"
            )
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
        print(stoptime)

        self.DATA.suiteDetail.at[0, "status"] = SuiteStatus
        self.DATA.suiteDetail.at[0, "s_end_time"] = stoptime

    def startSequence(self):
        """
        start running the testcases in sequence
        """
        for testcase in self.CONFIG.getTestcaseConfig():
            data = self.getTestcaseData(testcase)
            output, error = executorFactory(data)
            if error:
                logging.error(
                    f"Error occured while executing the testcase: {error['testcase']}"
                )
                logging.error(f"message: {error['message']}")
            self.update_df(output, error)

    def startParallel(self):
        """
        start runnig the testcases in parallel
        """
        pool = None
        try:
            pool = Pool(self.PARAMS.get("THREADS", DefaultSettings.THREADS))
            # decide the dependency order:
            for testcases in self.getDependency(self.CONFIG.getTestcaseConfig()):
                if len(testcases) == 0:
                    raise Exception("No testcase to run")
                poolList = []
                for testcase in testcases:

                    # only append testcases whose dependency are passed otherwise just update the database
                    if self.isDependencyPassed(testcase):
                        poolList.append(self.getTestcaseData(testcase.get("NAME")))
                    else:
                        dependencyError = {
                            "message": "dependency failed",
                            "testcase": testcase["NAME"],
                            "category": testcase.get("CATEGORY", None),
                            "product_type": testcase.get("PRODUCT_TYPE", None),
                        }

                        # update the testcase in the database with failed dependency
                        self.update_df(None, dependencyError)

                if len(poolList) == 0:
                    continue

                # runs the testcase in parallel here
                results = pool.map(executorFactory, poolList)
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
        except Exception as e:
            common.errorHandler(
                logging, e, "some Error Occurred while running the parallel testcases"
            )

        finally:
            if pool:
                pool.close()

    def update_df(self, output: List, error: Dict):
        """
        updates the testcase data in the dataframes
        """
        try:
            if error:
                output = self.getErrorTestcase(
                    error["message"],
                    error["testcase"],
                    error.get("category"),
                    error.get("product_type"),
                )
                output = [output]

            for i in output:
                i["testcaseDict"]["steps"] = i["jsonData"]["steps"]
                testcaseDict = i["testcaseDict"]
                # print("!!!!!!!!!!!!\n", testcaseDict, "\n!!!!!!!!!!")
                try:
                    self.testcaseData[testcaseDict.get("tc_run_id")] = i["jsonData"]
                except Exception as e:
                    print(e)

                self.DATA.testcaseDetails = self.DATA.testcaseDetails.append(
                    testcaseDict, ignore_index=True
                )
                self.updateTestcaseMiscData(
                    i["misc"], tc_run_id=testcaseDict.get("tc_run_id")
                )
                dataUpload.sendTestcaseData((self.DATA.totestcaseJson(testcaseDict.get("tc_run_id").upper(), self.s_run_id)), self.PARAMS["BRIDGE_TOKEN"])

        except Exception as e:
            common.errorHandler(logging, e, "in update_df")

    def getErrorTestcase(
        self,
        message: str,
        testcaseName: str,
        category: str = None,
        product_type: str = None,
    ) -> Dict:

        result = {}
        testcaseDict = {}
        misc = {}
        tc_run_id = f"{testcaseName}_{self.project_env}_{uuid.uuid4()}"
        tc_run_id = tc_run_id.upper()
        testcaseDict["tc_run_id"] = tc_run_id
        testcaseDict["status"] = status.FAIL.name
        testcaseDict["start_time"] = datetime.now(timezone.utc)
        testcaseDict["end_time"] = datetime.now(timezone.utc)
        testcaseDict["name"] = testcaseName
        testcaseDict["ignore"] = False
        if category:
            testcaseDict["category"] = category
        testcaseDict["log_file"] = None
        testcaseDict["result_file"] = None
        testcaseDict["user"] = self.user
        testcaseDict["machine"] = self.machine
        if product_type:
            testcaseDict["product_type"] = product_type

        result["testcaseDict"] = testcaseDict

        misc["reason of failure"] = message

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
        data = {}
        data["configData"] = self.CONFIG.getTestcaseData(testcase)
        data["PROJECTNAME"] = self.projectName
        data["ENV"] = self.project_env
        data["S_RUN_ID"] = self.s_run_id
        data["USER"] = self.user
        data["MACHINE"] = self.machine
        data["OUTPUT_FOLDER"] = self.testcase_folder
        return data

    def getDependency(self, testcases: Dict):
        """
        yields the testcases with least dependncy first
        Reverse toplogical sort
        """
        adjList = {
            key: list(value.get("DEPENDENCY", [])) for key, value in testcases.items()
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
                logging.error(
                    "circular dependency found please remove the cirular dependency"
                )
                logging.error("possible testcase with circular dependencies")
                logging.error(adjList.keys())
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
        for dep in testcase.get("DEPENDENCY", []):

            dep_split = dep.split(":")

            if len(dep_split) == 1:
                if dep_split[0] not in self.DATA.testcaseDetails["NAME"]:
                    return False

            else:
                if dep_split[0].upper() == "P":
                    if dep_split[1] not in self.DATA.testcaseDetails["NAME"]:
                        return False
                    if (
                        self.DATA.testcaseDetails.loc(
                            self.DATA.testcaseDetails["NAME"] == dep_split[1]
                        )["status"]
                        != status.PASS.name
                    ):
                        return False

                if dep_split[0].upper() == "F":
                    if dep_split[1] not in self.DATA.testcaseDetails["NAME"]:
                        return False
                    if (
                        self.DATA.testcaseDetails.loc(
                            self.DATA.testcaseDetails["NAME"] == dep_split[1]
                        )["status"]
                        != status.FAIL.name
                    ):
                        return False

        return True

    def makeReport(self):
        """
        saves the report json
        """
        suiteReport = None

        date = datetime.now().strftime("%Y_%b_%d_%H%M%S_%f")

        suite_path = os.path.dirname(__file__)
        suite_path = os.path.join(os.path.split(suite_path)[0], "final_report.html")
        with open(suite_path, "r") as f:
            suiteReport = f.read()

        reportJson = self.DATA.getJSONData()
        print(type(reportJson))
        reportJson = json.loads(reportJson)
        reportJson["TestStep_Details"] = self.testcaseData
        # self.testcaseData = json.dumps(self.testcaseData)
        reportJson = json.dumps(reportJson)
        print("------------ reportJson\n", reportJson)
        suiteReport = suiteReport.replace("DATA", reportJson)

        ResultFile = os.path.join(self.ouput_folder, "Result_{}.html".format(date))

        with open(ResultFile, "w+") as f:
            f.write(suiteReport)
