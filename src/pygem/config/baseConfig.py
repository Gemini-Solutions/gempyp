from abc import ABC, abstractmethod
from typing import Dict
import logging
from pygem.libs.common import errorHandler
from pygem.libs.exceptions import ParseException

class abstarctBaseConfig(ABC):

    _CONFIG = None

    def __init__(self,*args, **kwargs):
        try:
            self.parse(*args, **kwargs)
        except ParseException as e:
            errorHandler(logging, e, "failed to parse the config")
        
        except Exception as e:
            errorHandler(logging, e, "Some Error occured")

    def getSuiteConfig(self) -> Dict:

        return self._CONFIG["SUITE_DATA"]

    def getTestcaseConfig(self) -> Dict:
        return self._CONFIG["TESTCASE_DATA"]

    def getTestcaseData(self, testcaseName: str) -> Dict:
        return self._CONFIG["TESTCASE_DATA"].get(testcaseName, None) 

    
    @abstractmethod
    def parse(self, *args, **kwargs):
        """
            overrite this method
        """
        pass



    
    
    
    