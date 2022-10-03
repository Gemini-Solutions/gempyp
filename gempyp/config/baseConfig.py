from abc import ABC, abstractmethod
import traceback
from typing import Dict
import logging


class AbstarctBaseConfig(ABC):
    def __init__(self, *args, **kwargs):
        self._CONFIG = {}
        self.cli_config ={}
        self.total_yflag_testcase =0
        
        try:
            self.parse(*args, **kwargs)
            # filter removed from here because we need to apply filter after updating data with cli input(if given)
            # self.update()
            logging.info("----------- Xml parsing completed ------------")
        except Exception as e:
            traceback.print_exc()
            logging.error("failed to parse the config: {e}".format(e=e))

    def getSuiteConfig(self) -> Dict:
        # logging.info("^^^^^^^^^^^^^ \n {suite_data} \n^^^^^^^^^".format(suite_data=self._CONFIG["SUITE_DATA"]))
        self.filter()
        return self._CONFIG["SUITE_DATA"]

    def getTestcaseConfig(self) -> Dict:
        """reutrn the testCaseData to filter method"""
        # logging.info("--------testCaseDict--------\n {testcaseDict} \n----------".format(testcaseDict=self._CONFIG["TESTCASE_DATA"]))
        return self._CONFIG["TESTCASE_DATA"]

    def getTestcaseData(self, testcaseName: str) -> Dict:
        return self._CONFIG["TESTCASE_DATA"].get(testcaseName, None)
    

    def getTestcaseLength(self) -> int:
        """
        return the length of testCase
        """
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
        testcase_data = self.getTestcaseConfig()
        filtered_dict = {}
        ###code for passing testcases through cli jira-113
        if "TESTCASES" in self._CONFIG['SUITE_DATA']:
            test = {}
            testcase = self._CONFIG['SUITE_DATA']["TESTCASES"]
            if testcase[0] == '[':
                testcase = testcase[1:-1]
                testcase = testcase.split(",")
            else:
                testcase = testcase.split(",")
            for key, value in testcase_data.items():
                if key in testcase:
                    test[key] = value
            testcase_data = test

        for key, value in testcase_data.items():
            if value.get("RUN_FLAG", "N").upper() != "Y":
                continue
            if value.get("RUN_FLAG", "Y").upper() == "Y":
                self.total_yflag_testcase += 1
            if self.cli_config["CATEGORY"]!=None and value.get("CATEGORY") not in self.cli_config["CATEGORY"].split(","):
                continue
            if self.cli_config["SET"]!=None and value.get("SET") not in self.cli_config["SET"].split(","):
                print(value.get("SET"))
                continue
            

            # TODO add more filters
            
            if self.cli_config["CATEGORY"]!=None and value.get("CATEGORY") not in self.cli_config["CATEGORY"].split(","):
                print(value.get("CATEGORY"))
                continue
            if self.cli_config["SET"]!=None and value.get("SET") not in self.cli_config["SET"].split(","):
                print(value.get("SET"))
                continue

            filtered_dict[key] = value
        
        self._CONFIG["TESTCASE_DATA"] = filtered_dict

    # TODO
    def update(self):
        """to update the data that is passed by cli"""
        try:
            for element in self.cli_config.keys():
                if self.cli_config[element]:
                    if str(element) in self._CONFIG['SUITE_DATA']:
                        # print(element)
                        self._CONFIG['SUITE_DATA'][element] = self.cli_config[element]
                    else:
                        self._CONFIG['SUITE_DATA'][element] = self.cli_config[element]
        except Exception as error:
            print("error occurs in update",error)
        
        
