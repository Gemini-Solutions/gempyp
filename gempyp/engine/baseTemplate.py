from datetime import datetime, timezone
from typing import Dict
from gempyp.libs.enums.status import status
from gempyp.reporter.reportGenerator import TemplateData


class TestcaseReporter:
    """the class need to be extended by all the testcases"""

    def __init__(self, project_name: str = None, testcase_name: str = None):
        """initializes the reportfile to start making the report
        :param project_name: The name of the project. Will be overidden by the name
                            present in the config if the config is given.
        :param testcase_name: testcase name. Will be overidden by the name present in the
                            config if the config is present.
        :param destructor: to call the destructor function if True. if False user have to manually call the function.
        :param extraColumns: any extra column required in the result file
        """
        self.project_name = project_name.strip()
        self.testcase_name = testcase_name.strip()
        self.begin_time = datetime.now(timezone.utc)
        self.end_time = None
        self._misc_data = {}
        self.json_data = None
        self._is_destructor_called = False
        self.status_count = {k: 0 for k in status}
        self.template_data = TemplateData()
        self.logger = None

        # can be overiiden for custom result file
        self.result_file_name = None
        # can be overiiden or will be automatically decided in the end
        self.status = None

        # starting the new Report
        self.template_data.newReport(self.project_name, self.testcase_name)

    def addMisc(self, key: str, value):
        """
        add the misc data to the report by calling it as reporter.addMisc()
        takes two arguments one is column name and other one is value
        """
        if key in self._misc_data:
            if value in self._misc_data[key]:
                pass
            else:
                self._misc_data[key] = self._misc_data[key]+ ', ' + value
        else:
            self._misc_data[key] = value

    def getMisc(self, key: str):
        """
        returns the misc data for the sprcified key
        returns none if no data is found
        """
        return self._misc_data.get(key, None)

    def addRow(
        self,
        test_step: str,
        description: str,
        status: status,
        file: str = None,
        link_name: str = "Click Here",
        **kwargs,
    ):
        """
        add the new row to the report 
        takes three argument first is testname,second is description of test and third is status 
        calls the newRow method of reportGenerator 
        
        """
        self.status_count[status] += 1

        attachment = None
        if file:
            # link = self.addLink(file, linkName)
            attachment = {"URL": file, "linkName": link_name}
        # add the new row
        self.template_data.newRow(
            test_step, description, status.name, attachment=attachment, **kwargs
        )

    def addLink(self, file: str, linkName: str):
        """
        return the anchor tab instead of the link
        """
        # if you want to add the file to s3 we can do it here

        return f""" <a href='{file}'>{linkName}</a> """

    def finalizeReport(self):
        """
        the destructor after the call addRow will not work and will call finalizeResult method of reportGenerator file
        """
        # only call the destructor once
        if self._is_destructor_called:
            return
        self._is_destructor_called = True

        if not self.status:
            self.status = self.findStatus()
        self.end_time = datetime.now(timezone.utc)
        for key in list(self.status_count):
            if self.status_count[key] == 0:
                del self.status_count[key]
        self.template_data.finalizeResult(self.begin_time, self.end_time, self.status_count)

    def findStatus(self):
        """
        method will return whether the status is pass or fail or warn
        """
        for i in status:
            if self.status_count[i] > 0:
                return i.name

    def serialize(self) -> Dict:
        """
        used to assign some values to the variables that are further used in json that is uploaded to db
        takes values from reporter function and other variables in the same file
        """
        result_data = {}
        result_data["NAME"] = self.testcase_name
        result_data["PROJECT_NAME"] = self.project_name
        result_data["STATUS"] = self.status
        result_data["RESULT_FILE"] = self.result_file_name
        result_data["STEPS_COUNT"] = self.status_count
        result_data["MISC"] = self._misc_data
        result_data["START_TIME"] = self.begin_time
        result_data["END_TIME"] = self.end_time
        result_data["json_data"] = self.json_data
        return result_data
