import requests
import base64
import json
import os
from pygem.engine.simpleTestcase import AbstarctSimpleTestcase
from pygem.engine.baseTemplate import testcaseReporter
from pygem.libs.enums.status import status


class authenticate(AbstarctSimpleTestcase):
    def main(self, testcaseSettings, **kwargs):
        self.username = "kiran.kumari"
        self.passwd = "hello@2022"
        self.login_auth = None
        self.auth(kwargs["PROJECTNAME"], testcaseSettings["NAME"])
        return self.reporter

    def auth(self, projectName, testcaseName):
        login = '{0}:{1}'.format(self.username, self.passwd)
        login_bytes = login.encode("ascii")
        self.login_auth = base64.b64encode(login_bytes).decode()
        self.reporter = testcaseReporter(projectName, testcaseName)
        self.login()
    
    def login(self):
        auth_api = 'https://mymisapi.geminisolutions.in/api/Authenticate/Authenticate'
        response = requests.post(auth_api, headers={"Authorization": "Basic {0}".format(self.login_auth)})
        header = json.loads(response.text)
        print(header)
        print(type(header))
        header["Authorization"] = "Basic {0}".format(self.login_auth)
        self.reporter.addRow("Validate the Authentication API", auth_api, status.INFO)
        self.reporter.addRow("Validate the user", self.username, status.INFO)
        self.reporter.addRow("Validate the Authorization key", self.login_auth, status.INFO)
        if response.status_code >= 200 and response.status_code <300:
            self.reporter.addRow("Login successful", response.status_code, status.PASS, method="POST")
            os.environ["token"] = header["Token"]
        else:
            self.reporter.addRow("Login unsuccessful", "Username or password incorrect", status.FAIL, method="POST")

    
if __name__ == "__main__":
    authenticate().auth("test", "auth")





