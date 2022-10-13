
from ntpath import join
import tempfile
from typing import Dict
import lxml.etree as et
import logging
from gempyp.config.baseConfig import AbstarctBaseConfig
from gempyp.libs.parsers import xmlToDict, xmlToList
from gempyp.libs.logConfig import LoggingConfig
import sys, os
import warnings
import uuid

class XmlConfig(AbstarctBaseConfig):
    def __init__(self, filePath: str, s_run_id):
        
        # code pushed in parse function to make run_id working
        self.s_run_id = s_run_id
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

        self.log_dir = str(os.path.join(tempfile.gettempdir(), 'logs'))
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.unique_id = str(uuid.uuid4())
        if self.s_run_id != None:
             self.unique_id = self.s_run_id
        elif "RUN_ID" in self._CONFIG["SUITE_DATA"]:
            self.unique_id = self._CONFIG["SUITE_DATA"]["RUN_ID"]

        os.environ['unique_id'] = self.unique_id
        os.environ['log_dir'] = self.log_dir
        warnings.filterwarnings('ignore')
        suiteLogsLoc = str(os.path.join(self.log_dir, 'Suite_' + self.unique_id + '.log'))
        LoggingConfig(os.path.join(self.log_dir, 'Suite_' + self.unique_id + '.log'))
        # LoggingConfig(suiteLogsLoc)
        print("------suite logs------",suiteLogsLoc)


        self._CONFIG["TESTCASE_DATA"] = self._getTestCaseData(data)
        self._CONFIG["SUITE_DATA"]['LOG_DIR'] = self.log_dir
        self._CONFIG["SUITE_DATA"]['UNIQUE_ID'] = self.unique_id

    def _getSuiteData(self, data) -> Dict:

        suite_data = data.find("suite")

        suite_dict = xmlToDict(suite_data)
        suite_dict["SUITE_VARS"] = {}
        logging.info("--------suite_dict--------\n {suite_dict} \n----------".format(suite_dict=suite_dict))
        # do your validations here

        return suite_dict

    def _getTestCaseData(self, data) -> Dict:

        testcase_data = data.find("testcases")

        testcase_list = xmlToList(testcase_data)
        testcase_dict = {k['NAME']: k for k in testcase_list}
        # do your validation here

        return testcase_dict
