from typing import List
from datetime import datetime
import logging
import atexit
import tempfile
from pygem.libs.enums.status import status
import reportGenerator



class baseTemplate():
    """ the class need to be extended by all the testcases"""

    def __init__(self,projectName: str = None, testcaseName: str = None, destructor: bool = False, extraColumns : List = None):
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
        self.destructor = destructor
        self.extraColumns = extraColumns
        self.beginTime = datetime.utcnow()
        self.statusCount = {k:0 for k in status}

        self.RESULTFILE = tempfile.NamedTemporaryFile(mode='w+', encoding="iso-8859-1")
        
        # can be overiiden for custom result file
        self.resultFileName = self.RESULTFILE.name
        # can be overiiden or will be automatically decided in the end
        self.status = None

        # starting the new Report
        reportGenerator.newReport(self.projectName, self.testcaseName, self.RESULTFILE,self.extraColumns)
        # register the destructor
        if self.destructor:
            atexit.register(self.destructor)

    
    def addRow(self, testStep: str, description: str, status: status,  file: str = None, linkName: str ="Click Here", **kwargs):
        """
            add the new row to the file
        """
        self.statusCount[status]+=1

        link = None
        if file:
            link = self.addLink(file, linkName)

        # add the new row        
        reportGenerator.newRow(testStep, description, status, resultFile = self.RESULTFILE, link=link, **kwargs)



    def addLink(self, file: str, linkName: str):
        """
            return the anchor tab instead of the link
        """
        # if you want to add the file to s3 we can do it here

        return f""" <a href='{file}'>{linkName}</a> """

    def destructor(self):
        """
            the destructor after the call addRow will not work
        """

        # closing the resultfile
        if self.RESULTFILE:
            self.RESULTFILE.close()

        if not self.status:
            self.status = self.findStatus()
        
        #TODO
        reportGenerator.finalizeResult()
        self.generateJSON()

    

    def findStatus(self):
        if self.statusCount[status.FAIL] > 0:
            return status.FAIL
        elif self.statusCount[status.WARN] > 0:
            return status.WARN
        elif self.statusCount[status.PASS] > 0:
            return status.PASS
        else:
            return status.INFO


    def generateJSON(self):
        """
            generates the end result json
        """
        pass        


        

    
    


    



