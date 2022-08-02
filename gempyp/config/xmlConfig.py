from importlib.resources import path
from ntpath import join
import tempfile
from typing import Dict
import lxml.etree as et
import logging
from gempyp.config.baseConfig import abstarctBaseConfig
from gempyp.libs.parsers import xmlToDict, xmlToList
from gempyp.libs.logConfig import LoggingConfig
import sys, os
import warnings
import uuid

class XmlConfig(abstarctBaseConfig):
    def __init__(self, filePath: str):
        
        self.log_dir = str(os.path.join(tempfile.gettempdir(), 'logs'))
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.unique_id = str(uuid.uuid4())
        os.environ['unique_id'] = self.unique_id
        os.environ['log_dir'] = self.log_dir
        warnings.filterwarnings('ignore')
        suiteLogsLoc = str(os.path.join(self.log_dir, 'Suite_' + self.unique_id + '.log'))
        LoggingConfig(os.path.join(self.log_dir, 'Suite_' + self.unique_id + '.log'))
        # LoggingConfig(suiteLogsLoc)
        print("------suite logs------",suiteLogsLoc)
        super().__init__(filePath)
        # do any xml specific validatioins here
       

    def parse(self, filePath):
        logging.info("-------- Xml file path: {filePath} ----------".format(filePath=filePath))
        path_list = filePath.split(os.sep)[0:-1]
        newfilePath = os.sep.join(path_list)
        sys.path.append({"XMLConfigDir":newfilePath})

        logging.info("-------- Started the Xml parsing in XmlConfig ---------")
        data = et.parse(filePath)
        self._CONFIG["SUITE_DATA"] = self._getSuiteData(data)        
        self._CONFIG["TESTCASE_DATA"] = self._getTestCaseData(data)
        self._CONFIG["SUITE_DATA"]['LOG_DIR'] = self.log_dir
        self._CONFIG["SUITE_DATA"]['UNIQUE_ID'] = self.unique_id

    def _getSuiteData(self, data) -> Dict:

        suiteData = data.find("suite")

        suiteDict = xmlToDict(suiteData)
        suiteDict["SUITE_VARS"] = {}
        #Adding bridgeToken validation here
        logging.info("--------suiteDict--------\n {suiteDict} \n----------".format(suiteDict=suiteDict))
        # if suiteDict.get("BRIDGE_TOKEN", None) is None:
        #     logging.critical("Bridge Token is Missing")
        #     sys.exit("ERROR: Bridge Token is Missing in the config.")
        # if suiteDict.get("USERNAME", None) is None:
        #     logging.critical("Username is Missing")
        #     sys.exit("ERROR: Username is Missing in the config.")
        # do your validations here

        return suiteDict

    def _getTestCaseData(self, data) -> Dict:

        testcaseData = data.find("testcases")
        testcaseList = xmlToList(testcaseData)
        testcaseDict = {k['NAME']: k for k in testcaseList}
        # do your validation here
        return testcaseDict
