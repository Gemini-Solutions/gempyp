import sys
import os
import logging
import platform
import getpass
import multiprocessing as Pool
from typing import Dict, List, Tuple, Type
import uuid
from datetime import datetime, timezone
from pygem.config.baseConfig import abstarctBaseConfig
from testData import testData
from pygem.libs.enums.status import status
from pygem.libs import common
from pygem.config import DefaultSettings


def executorFactory(data: Dict) -> Tuple(Dict, Dict):
    """
    calls the differnt executors based on the type of the data
    """
    # TODO have to decide the type of the variable
    if data["configData"]["type"].upper() == "DVM":
        # TODO do the DVM stuff
        logging.info("starting the DVM testcase")
    elif data["configData"]["type"].upper() == "RESTTEST":
        # TODO do the resttest stuff here
        logging.info("starting the resttest testcase")

    else:
        # TODO call the pygem testcases
        logging.info("starting the pygem testcases")


class Engine:
    def __init__(self, params_config):
        self.run(self, params_config)
        pass

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
        self.start()
        self.updateSuiteData()
        self.cleaup()

    def setUP(self, config: Type[abstarctBaseConfig]):
        self.PARAMS = config.getSuiteConfig()
        self.CONFIG = config
        self.machine = platform.node()
        self.user = getpass.getuser()
        self.current_dir = os.getcwd()
        self.platform = platform.system()
        self.start_time = datetime.now(timezone.utc)
        self.projectName = self.PARAMS["project"]
        self.project_env = self.PARAMS["env"]

        if "outputfolder"  in self.PARAMS:
            self.output_folder = self.PARAMS["outputFolder"]
            if not os.path.isdir(self.output_folder):
                os.makedirs(self.output_folder)
        else:
            self.output_folder = os.path.join(self.current_dir, "pygem_reports")
            os.makedirs(self.output_folder)

    def parseMails(self):
        self.mail = common.parseMails(self.PARAMS["mail"])

    def makeSuiteDetails(self):

        self.s_run_id = f"{self.projectName}_{self.project_env}_{uuid.uuid4()}"
        self.s_run_id = self.s_run_id.upper()
        SuiteDetails = {
            "s_run_id": self.s_run_id,
            "s_start_time": self.start_time,
            "s_end_time": None,
            "status": status.EXE.name,
            "project_name": self.projectName,
            "run_type": "ON DEMAND",
            "s_report_type": self.reportName,
            "user": self.user,
            "env": self.project_env,
            "machine": self.machine,
            "initiated_by": self.user,
            "run_mod": "LINUX_CLI",
        }
        self.DATA.suiteDetail = self.DATA.suiteDetail.append(
            SuiteDetails, ignore_index=True
        )

    def start(self):

        # check the mode and start the testcases accordingly

        try:
            if self.CONFIG.getTestcaseLength() <= 0:
                raise Exception("no testcase found to run")

            if self.PARAMS["mode"].upper() == "SEQUENCE":
                self.startSequence()
            if self.PARAMS["mode"].upper() == "OPTIMIZE":
                self.startParallel()
            else:
                raise TypeError("mode can only be sequence of parallel")

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
            self.DATA.testcaseDetails["end_time"].sort_values(ascending=False).iloc(0)
        )

        self.DATA.suiteDetail.at[0, "status"] = SuiteStatus
        self.DATA.suiteDetail.at[0, "end_time"] = stoptime

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
            pool = Pool(self.PARAMS.get("threads", DefaultSettings.THREADS))
            # decide the dependency order:
            for testcases in self.getDependency(self.CONFIG.getTestcaseConfig()):
                if len(testcases) == 0:
                    raise Exception("No testcase to run")
                poolList = []
                for testcase in testcases:

                    # only append testcases whose dependency are passed otherwise just update the database
                    if self.isDependencyPassed(testcase):
                        poolList.append(self.getTestcaseData(testcase))
                    else:
                        dependencyError = {
                            "message": "dependency failed",
                            "testcase": testcase["name"],
                            "category": testcase.get("category", None),
                            "product_type": testcase.get("product_type", None),
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
        if error:
            output = self.getErrorTestcase(
                error["message"],
                error["testcase"],
                error.get("category"),
                error.get("product_type"),
            )
            output = [output]

        for i in output:
            testcaseDict = i["testcaseDict"]
            self.DATA.testcaseDetails = self.DATA.testcaseDetails.append(
                testcaseDict, ignore_index=True
            )
            self.updateTestcaseMiscData(
                i["misc"], tc_run_id=testcaseDict.get("tc_run_id")
            )

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
        data["projectName"] = self.projectName
        data["project_env"] = self.project_env
        data["s_run_id"] = self.s_run_id
        data["user"] = self.user
        data["machine"] = self.machine
        data["env"] = self.project_env

        return data

    def getDependency(self, testcases: Dict):
        """
        yields the testcases with least dependncy first
        Reverse toplogical sort
        """
        adjList = {key: list(value.get("dependency", [])) for key, value in testcases}

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
            top_dep.update(key for key, value in adjList if not value)

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
        for dep in testcase.get("dependency", []):

            dep_split = dep.split(":")

            if len(dep_split) == 1:
                if dep_split[0] not in self.DATA.testcaseDetails["name"]:
                    return False

            else:
                if dep_split[0].upper() == "P":
                    if dep_split[1] not in self.DATA.testcaseDetails["name"]:
                        return False
                    if (
                        self.DATA.testcaseDetails.loc(
                            self.DATA.testcaseDetails["name"] == dep_split[1]
                        )["status"]
                        != status.PASS.name
                    ):
                        return False

                if dep_split[0].upper() == "F":
                    if dep_split[1] not in self.DATA.testcaseDetails["name"]:
                        return False
                    if (
                        self.DATA.testcaseDetails.loc(
                            self.DATA.testcaseDetails["name"] == dep_split[1]
                        )["status"]
                        != status.FAIL.name
                    ):
                        return False

            return True

    def cleaup(self):
        pass
