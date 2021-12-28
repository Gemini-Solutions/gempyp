from abc import ABC, abstractmethod
from typing import Dict
import logging
import argparse
from pygem.libs.common import errorHandler
from pygem.libs.exceptions import ParseException

class abstarctBaseConfig(ABC):



    def __init__(self,*args, **kwargs):
        self._CONFIG = None
        try:
            self.parse(*args, **kwargs)
        except ParseException as e:
            errorHandler(logging, e, "failed to parse the config")
        
        except Exception as e:
            errorHandler(logging, e, "Some Error occured")
        # filter the testcasesData
        self.filter()

    def getSuiteConfig(self) -> Dict:

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
            overrite this method
        """
        pass

    def filter(self):
        """
            filter the testcases that need to be ignored based on the run value and category sets
        """
        testcaseData = self.getTestcaseConfig()
        filteredDict = {}

        for key, value in testcaseData.items():
            if value.get("RUN_FLAG",'N').upper() != "Y":
                continue
            # TODO add more filters
        
            filteredDict[key] = value
        
        self._CONFIG["TESTCASE_DATA"] = filteredDict





    #TODO
    def update(self):
        """
            update the suiteData that is given in CLI inputs
        """
        pass

        



    
    
    
    