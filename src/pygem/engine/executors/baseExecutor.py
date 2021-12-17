from abc import ABC, abstractmethod
from typing import Dict
class abstaractExecutor(ABC):

    @abstractmethod
    def execute(self, testcaseSettings: Dict) -> Dict:
        """
            the method which will run the single testcase file and parses the results.
            this method can be run in parallel
            its implemetations can run somewhere else getting the settings from a message queue
        """
        pass