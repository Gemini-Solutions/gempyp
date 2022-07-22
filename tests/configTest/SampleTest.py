import requests
import os
import json
from gempyp.engine.simpleTestcase import AbstractSimpleTestcase
from gempyp.engine.baseTemplate import testcaseReporter
from gempyp.libs.enums.status import status


class fetchBridgeToken(AbstractSimpleTestcase):
    def main(self, testcaseSettings, **kwargs):
        self.reporter = testcaseReporter(kwargs["project"], testcaseSettings["tcname"])
        self.fetchBridgeToken()
        return self.reporter

    def fetchBridgeToken(self):
        api = 'http://ec2-3-108-218-108.ap-south-1.compute.amazonaws.com:8080/bridge/token'
        self.reporter.addRow("Bridge Token API", "To fetch To fetch bridge token from our database.", status.INFO)
        self.reporter.addRow("Validate the Bridge Token API", api, status.INFO)
        try:
            jwt = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ12cVyMTIzIiwiaWF0IjoxNjUwNjUyMDA1LCJleHAiOjE2NTA2NTIzMDV9.OkEdaPetEhqJZW6i4mAgVVfcKIvQ8Te0i_2s_ktjJyuQU_8SyjmyoSndDW5suDTnhlxLYNrq5z3gg5u8_PRtJg"
            response = requests.get(api, headers={"Authorization": "Bearer {}".format(jwt)})
            if response.status_code == 200:
                res = json.loads(response.text)
                self.reporter.addRow("Validate the Bridge Token", res["data"]["bridgeToken"], status.PASS, method="POST")
            elif response.status_code == 403:
                self.reporter.addRow("Validate the Bridge Token", "Bearer Token incorrect: {}".format(response.status_code), status.FAIL, method="POST")
            else:
                self.reporter.addRow("Validate the Bridge Token", "Bridge Token could nt be fetched: {}".format(response.status_code), status.FAIL, method="POST")
        except Exception as e:                  
            self.reporter.addRow("Some Error while running the API", e, status.FAIL)

                


        