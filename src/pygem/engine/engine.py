import os
import logging
import platform
import getpass
import multiprocessing as Pool
from typing import Dict, Tuple, Type
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

            # update the suiteDetails:

        except Exception as e:
            # TODO
            pass

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
            for testcases in self.getDependency():
                if len(testcases) == 0:
                    raise Exception("No testcase to run")
                poolList = []
                for testcase in testcases:
                    poolList.append(self.getTestcaseData(testcase))

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

    def update_df(self, output: Dict, error: Dict):
        """
        updates the testcase data in the dataframes
        """
        if error:
            output = self.getErrorTestcase(
                error["message"], error["testcase"], error.get("category"), error.get("product_type")
            )

        testcaseDict = output["testcaseDict"]
        self.DATA.testcaseDetails = self.DATA.testcaseDetails.append(
            testcaseDict, ignore_index=True
        )
        self.updateTestcaseMiscData(
            output["misc"], tc_run_id=testcaseDict.get("tc_run_id")
        )

    def getErrorTestcase(self, message: str, testcaseName: str, category: str = None, product_type: str = None) -> Dict:
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


    def updateTestcaseMiscData(misc, tc_run_id):
        """
            updates the misc data for the testcases
        """
        miscList = []

        



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

    def cleaup(self):
        pass
