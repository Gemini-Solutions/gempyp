from abc import ABC, abstractmethod
import traceback
from typing import Dict
import logging
import os


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
        return self._CONFIG["TESTCASE_DATA"].get(testcaseName.upper(), None)  ## uppercase
    
    def getSubTestcaseData(self, testcaseName: str) -> Dict:
        return self._CONFIG["SUBTESTCASES_DATA"].get(testcaseName.upper(), None)  ## uppercase

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
                testcase = [i.strip(" ").upper() for i in testcase.split(",")]  ## uppercase
            else:
                testcase = [i.strip(" ").upper() for i in testcase.split(",")]  ## uppercase
            for key, value in testcase_data.items():
                if key in testcase:
                    test[key] = value
            testcase_data = test

        for key, value in testcase_data.items():
            testcases = ""
            if(value.get("RUN_FLAG", "N").upper()=="Y" and "SUBTESTCASES" in value.keys()):
                testcases=value.get("SUBTESTCASES").upper().split(",")  ## uppercase
                testcases.append(key)
            if value.get("RUN_FLAG", "N").upper() != "Y":
                continue
            if value.get("RUN_FLAG", "Y").upper() == "Y":
                self.total_yflag_testcase += 1
            
            if self.filter_category(value):
                print("here")
                continue
            if self._CONFIG.get("SUITE_DATA",None).get("CATEGORY",None)!=None and value.get("CATEGORY") not in self._CONFIG.get("SUITE_DATA",None).get("CATEGORY",None).split(","):
                continue


            filtered_dict[key] = value
            
            if(len(testcases)>0):
                for i in range(len(testcases)):
                    if(testcases[i] in testcase_data.keys()):
                        filtered_dict_subtestcases[testcases[i]]=testcase_data.get(testcases[i])
        self._CONFIG["SUBTESTCASES_DATA"] = filtered_dict_subtestcases
       
    
        self._CONFIG["TESTCASE_DATA"] = filtered_dict

    def filter_category(self, value):
        """ filtering the categories that we want to run, if any. Returns 0 if we want to run the testcase"""
        
        exp_category = None
        this_category = []
        if self.cli_config.get("CATEGORY", None):
            exp_category = self.cli_config["CATEGORY"] if isinstance(self.cli_config["CATEGORY"], list) else str(self.cli_config["CATEGORY"]).upper().split(",")
        if value.get("CATEGORY", None):
            this_category = value.get("CATEGORY") if isinstance(value.get("CATEGORY"), list) else str(value.get("CATEGORY")).upper().split(",")
        if exp_category:
            if not len(list(set(exp_category) & set(this_category))) < 1:
                return 1
        return 0

    # TODO
    def update(self):
        """to update the data that is passed by cli"""
        try:
            for key in self._CONFIG['SUITE_DATA'].get('ENV-VARS',None):
                os.environ[key] = self._CONFIG['SUITE_DATA'].get('ENV-VARS',None).get(key,None)
        except Exception as error:
            print("Error in updating environment variable",error)
        try:
            for key in self._CONFIG['SUITE_DATA'].keys():
                value=self._CONFIG['SUITE_DATA'][key]
                if("$[#ENV." in value):
                        envValue=value
                        value=value.strip("$[#ENV.").strip("]")
                        self._CONFIG['SUITE_DATA'][key]=os.environ.get(value)
                        self._CONFIG['SUITE_DATA']["SUITE_VARS"][envValue.strip("$[#").strip("]").replace(".","_").upper()]=os.environ.get(value)
                if("$[#" in value):
                        value=value.strip("$[#").strip("]")
                        self._CONFIG['SUITE_DATA'][key]=os.environ.get(value)
          

        except Exception as error:
            print("error occurs in finding environment variable",error)
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
        
        
