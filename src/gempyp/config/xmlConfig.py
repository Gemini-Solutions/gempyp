from typing import Dict
import lxml.etree as et
from gempyp.config.baseConfig import abstarctBaseConfig
from gempyp.libs.parsers import xmlToDict, xmlToList
import sys


class XmlConfig(abstarctBaseConfig):
    def __init__(self, filePath: str):
        super().__init__(filePath)
        # do any xml specific validatioins here

    def parse(self, filePath):
        print("-------- path", filePath)
        data = et.parse(filePath)
        self._CONFIG["SUITE_DATA"] = self._getSuiteData(data)
        self._CONFIG["TESTCASE_DATA"] = self._getTestCaseData(data)

    def _getSuiteData(self, data) -> Dict:

        suiteData = data.find("suite")

        suiteDict = xmlToDict(suiteData)
        #Adding bridgeToken validation here
        print("-------------- suiteDict\n", suiteDict, "\n----------")
        if suiteDict.get("BRIDGE_TOKEN", None) is None:
            sys.exit("ERROR: Bridge Token is Missing in the config.")
        # do your validations here

        return suiteDict

    def _getTestCaseData(self, data) -> Dict:

        testcaseData = data.find("testcases")

        testcaseList = xmlToList(testcaseData)

        testcaseDict = {k["NAME"]: k for k in testcaseList}
        # do your validation here

        return testcaseDict
