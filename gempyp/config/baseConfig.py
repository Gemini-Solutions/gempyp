from abc import ABC, abstractmethod
import traceback
from typing import Dict
import argparse
import logging

class abstarctBaseConfig(ABC):
    def __init__(self, *args, **kwargs):
        self._CONFIG = {}
        self.cli_config ={}
        try:
            self.parse(*args, **kwargs)
            # filter the testcasesData
            self.filter()
            logging.info("----------- Xml parsing completed ------------")
        except Exception as e:
            traceback.print_exc()
            logging.error("failed to parse the config: {e}".format(e=e))

    def getSuiteConfig(self) -> Dict:
        # logging.info("^^^^^^^^^^^^^ \n {suite_data} \n^^^^^^^^^".format(suite_data=self._CONFIG["SUITE_DATA"]))
        return self._CONFIG["SUITE_DATA"]

    def getTestcaseConfig(self) -> Dict:
        # logging.info("--------testCaseDict--------\n {testcaseDict} \n----------".format(testcaseDict=self._CONFIG["TESTCASE_DATA"]))
        return self._CONFIG["TESTCASE_DATA"]

    def getTestcaseData(self, testcaseName: str) -> Dict:
        return self._CONFIG["TESTCASE_DATA"].get(testcaseName, None)
    

    def getTestcaseLength(self) -> int:
        return len(self._CONFIG.get("TESTCASE_DATA", []))

    @abstractmethod
    def parse(self, *args, **kwargs):
        """
        override this method in xmlConfig
        """
        pass

    def filter(self):
        """
        filter the testcases that need to be ignored based on the run value and category sets
        """
        testcaseData = self.getTestcaseConfig()
        filteredDict = {}

        for key, value in testcaseData.items():
            if value.get("RUN_FLAG", "N").upper() != "Y":
                continue
            # TODO add more filters

            filteredDict[key] = value

        self._CONFIG["TESTCASE_DATA"] = filteredDict

    # TODO
    def update(self):
        try:
            for element in self.cli_config.keys():
                if self.cli_config[element]:
                    if str(element) in self._CONFIG['SUITE_DATA']:
                        self._CONFIG['SUITE_DATA'][element] = self.cli_config[element]
        except Exception as error:
            print("error occurs in update",error)
        """
        update the suiteData that is given in CLI inputs
        """
        
