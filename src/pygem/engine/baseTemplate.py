from typing import Dict, List
from abc import ABC,abstractmethod
from datetime import datetime, timezone
import logging
from pygem.libs.enums.status import status
from pygem.config import DefaultSettings 
from pygem.engine.reportGenerator import templateData

class baseTemplate(ABC):
    """ the class need to be extended by all the testcases"""

    def __init__(self,projectName: str = None, testcaseName: str = None):
        """ initializes the reportfile to start making the report 
            :param projectName: The name of the project. Will be overidden by the name 
                                present in the config if the config is given.
            :param testcasename: testcase name. Will be overidden by the name present in the 
                                config if the config is present.
            :param destructor: to call the destructor function if True. if False user have to manually call the function.
            :param extraColumns: any extra column required in the result file
        """
        self.projectName = projectName.strip()
        self.testcaseName = testcaseName.strip()
        self.beginTime = datetime.now(timezone.utc)
        self.endTime = None
        self.statusCount = {k:0 for k in status}
        self.templateData = templateData()
        
        # can be overiiden for custom result file
        self.resultFileName = None
        # can be overiiden or will be automatically decided in the end
        self.status = None

        # starting the new Report
        self.templateData.newReport(self.projectName, self.testcaseName)
    
    def addRow(self, testStep: str, description: str, status: status,  file: str = None, linkName: str ="Click Here", **kwargs):
        """
            add the new row to the file
        """
        self.statusCount[status]+=1

        attachment = None
        if file:
            # link = self.addLink(file, linkName)
            attachment = {
                "URL": file,
                "linkName": linkName
            }
        # add the new row
        self.templateData.newRow(testStep, description, status.name, attachment, **kwargs)




    def addLink(self, file: str, linkName: str):
        """
            return the anchor tab instead of the link
        """
        # if you want to add the file to s3 we can do it here

        return f""" <a href='{file}'>{linkName}</a> """

    def finalize_report(self):
        """
            the destructor after the call addRow will not work
        """

        if not self.status:
            self.status = self.findStatus()
        self.endTime = datetime.now(timezone.ut)
        
        self.templateData.finalizeResult(self.beginTime, self.endTime, self.statusCount)

    def findStatus(self):
        if self.statusCount[status.FAIL] > 0:
            return status.FAIL
        elif self.statusCount[status.WARN] > 0:
            return status.WARN
        elif self.statusCount[status.PASS] > 0:
            return status.PASS
        else:
            return status.INFO
    
    def _toJSON(self, resultFile):


    @abstractmethod
    def main(self, testcaseSettings: Dict):
        """
            extend the baseTemplate and implement this method.
        """

    
    def RUN(self, testcaseSettings):
        """
            the main function which will be called by the executor
        """
        # set the values from the report if not set automatically 
        if not self.projectName:
            self.projectName = testcaseSettings.get("PROJECTNAME", "PYGEM")

        if not self.testcaseName:
            self.testcaseName = testcaseSettings.get("TESTCASENAME", "TESTCASE")

        self.main(testcaseSettings)
        self.finalize_report()
        resultFile = self.templateData.makeReport(testcaseSettings.get("PYGEMFOLDER", DefaultSettings.DEFAULT_PYGEM_FOLDER))
        result = self._toJSON(resultFile)

        return result

        


        

    
    


    



