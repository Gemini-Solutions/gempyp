from abc import ABC, abstractmethod
from typing import Dict
import logging
import argparse
from gempyp.libs.common import errorHandler
from gempyp.libs.exceptions import ParseException

class abstarctBaseConfig(ABC):
    def __init__(self, *args, **kwargs):
        self._CONFIG = {}
        self.cli_config ={}
        try:
            self.parse(*args, **kwargs)
            # filter the testcasesData
            self.filter()
        except ParseException as e:
            errorHandler(logging, e, "failed to parse the config")

        except Exception as e:
            errorHandler(logging, e, "Some Error occured")

    def getSuiteConfig(self) -> Dict:
        
        print("^^^^^^^^^^^^^ \n ", self._CONFIG["SUITE_DATA"], "\n^^^^^^^^^")
        return self._CONFIG["SUITE_DATA"]

    def getTestcaseConfig(self) -> Dict:
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
        
