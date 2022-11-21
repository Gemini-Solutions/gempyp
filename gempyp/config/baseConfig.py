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
    
    def getSubtestcasesConfig(self) -> Dict:
       

        return self._CONFIG["SUBTESTCASES_DATA"]

    def getTestcaseData(self, testcaseName: str) -> Dict:
        return self._CONFIG["TESTCASE_DATA"].get(testcaseName, None)
    
    def getSubTestcaseData(self, testcaseName: str) -> Dict:
        return self._CONFIG["SUBTESTCASES_DATA"].get(testcaseName, None)

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
        filtered_dict_subtestcases = {}

        ###code for passing testcases through cli jira-113
        if "TESTCASE_LIST" in self._CONFIG['SUITE_DATA']:
            test = {}
            testcase = self._CONFIG['SUITE_DATA']["TESTCASE_LIST"]
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
            testcases = ""
            if(value.get("RUN_FLAG", "N").upper()=="Y" and "SUBTESTCASES" in value.keys()):
                testcases=value.get("SUBTESTCASES").split(",")
                testcases.append(key)
            if value.get("RUN_FLAG", "N").upper() != "Y":
                continue
            if value.get("RUN_FLAG", "Y").upper() == "Y":
                self.total_yflag_testcase += 1
            if self.cli_config["CATEGORY"]!=None and value.get("CATEGORY") not in self.cli_config["CATEGORY"].split(","):
                continue


            filtered_dict[key] = value
            
            if(len(testcases)>0):
                for i in range(len(testcases)):
                    if(testcases[i] in testcase_data.keys()):
                        filtered_dict_subtestcases[testcases[i]]=testcase_data.get(testcases[i])
        self._CONFIG["SUBTESTCASES_DATA"] = filtered_dict_subtestcases
       
    
        self._CONFIG["TESTCASE_DATA"] = filtered_dict

    # TODO
    def update(self):
        """to update the data that is passed by cli"""
        try:
            for element in self.cli_config.keys():
                if self.cli_config[element]:
                    if str(element) in self._CONFIG['SUITE_DATA']:
                        if(element=="ENV" and len(self.cli_config[element].split(","))>0):
                            self._CONFIG['SUITE_DATA']["ENV"]=self.cli_config[element].split(",")[0]
                            self._CONFIG['SUITE_DATA'][self.cli_config[element].split(",")[0].upper()]=self.cli_config[element].split(",")[1]
                        else:
                            self._CONFIG['SUITE_DATA'][element] = self.cli_config[element]
                    else:
                        self._CONFIG['SUITE_DATA'][element] = self.cli_config[element]
        except Exception as error:
            print("error occurs in update",error)
        
        
