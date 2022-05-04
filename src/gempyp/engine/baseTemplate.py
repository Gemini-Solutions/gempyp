from datetime import datetime, timezone
from typing import Dict
from gempyp.libs.enums.status import status
from gempyp.engine.reportGenerator import templateData


class testcaseReporter:
    """the class need to be extended by all the testcases"""

    def __init__(self, projectName: str = None, testcaseName: str = None):
        """initializes the reportfile to start making the report
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
        self._miscData = {}
        self.jsonData = None
        self._isDestructorCalled = False
        self.statusCount = {k: 0 for k in status}
        self.templateData = templateData()

        # can be overiiden for custom result file
        self.resultFileName = None
        # can be overiiden or will be automatically decided in the end
        self.status = None

        # starting the new Report
        self.templateData.newReport(self.projectName, self.testcaseName)

    def addMisc(self, key: str, value):
        """
        add the misc data to the report
        """
        self._miscData[key] = value

    def getMisc(self, key: str):
        """
        returns the misc data for the sprcified key
        returns none if no data is found
        """

        return self._miscData.get(key, None)

    def addRow(
        self,
        testStep: str,
        description: str,
        status: status,
        file: str = None,
        linkName: str = "Click Here",
        **kwargs,
    ):
        """
        add the new row to the file
        """
        self.statusCount[status] += 1

        attachment = None
        if file:
            # link = self.addLink(file, linkName)
            attachment = {"URL": file, "linkName": linkName}
        # add the new row
        self.templateData.newRow(
            testStep, description, status.name, attachment=attachment, **kwargs
        )

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
        # only call the destructor once
        if self._isDestructorCalled:
            return
        self._isDestructorCalled = True

        if not self.status:
            self.status = self.findStatus()
        self.endTime = datetime.now(timezone.utc)
        for key in list(self.statusCount):
            if self.statusCount[key] == 0:
                del self.statusCount[key]
        self.templateData.finalizeResult(self.beginTime, self.endTime, self.statusCount)

    def findStatus(self):

        for i in status:
            if self.statusCount[i] > 0:
                return i.name

        """
        if self.statusCount[status.FAIL] > 0:
            return status.FAIL
        elif self.statusCount[status.WARN] > 0:
            return status.WARN
        elif self.statusCount[status.PASS] > 0:
            return status.PASS
        else:
            return status.INFO
        """

    def serialize(self) -> Dict:
        resultData = {}
        resultData["NAME"] = self.testcaseName
        resultData["PROJECTNAME"] = self.projectName
        resultData["STATUS"] = self.status
        resultData["RESULT_FILE"] = self.resultFileName
        resultData["STEPS_COUNT"] = self.statusCount
        resultData["MISC"] = self._miscData
        resultData["START_TIME"] = self.beginTime
        resultData["END_TIME"] = self.endTime
        resultData["jsonData"] = self.jsonData

        return resultData
