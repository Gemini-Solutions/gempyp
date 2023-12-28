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
import json
from gempyp.config.customParser import CustomXMLParser
from lxml import etree
class XmlConfig(AbstarctBaseConfig):
    def __init__(self, filePath: str, s_run_id):
        
        # code pushed in parse function to make run_id working
        self.s_run_id = s_run_id
        super().__init__(filePath)
        # do any xml specific validatioins here

    def ignore_comments_and_parse(xml_file):
        parser = et.XMLParser(target=et.TreeBuilder(), comment_handler=lambda *args: None)
        tree = et.parse(xml_file, parser=parser)
        return tree
       

    def parse(self, file_paths):
        
        for filePath in file_paths:
            logging.info("-------- Xml file path: {filePath} ----------".format(filePath=filePath))
            path_list = filePath.split(os.sep)[0:-1]
            newfilePath = os.sep.join(path_list)
            sys.path.append({"XMLConfigDir":newfilePath})
            logging.info("-------- Started the Xml parsing in XmlConfig ---------")
            filePath=self.handleSpecialSymbols(filePath)
            # data = et.parse(filePath)
            parser = CustomXMLParser(remove_comments=True)
            data = etree.parse(filePath, parser=parser)
            if "SUITE_DATA" not in self._CONFIG:
                self._CONFIG["SUITE_DATA"] = self._getSuiteData(data)        

            self.log_dir = str(os.path.join(tempfile.gettempdir(), 'logs'))
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
            self.unique_id = str(uuid.uuid4())
            if self.s_run_id != None:
                self.unique_id = self.s_run_id
            elif "S_RUN_ID" in self._CONFIG["SUITE_DATA"]:
                self.unique_id = self._CONFIG["SUITE_DATA"]["S_RUN_ID"]
            os.environ['unique_id'] = self.unique_id
            os.environ['log_dir'] = self.log_dir
            warnings.filterwarnings('ignore')
            suiteLogsLoc = str(os.path.join(self.log_dir, 'Suite_' + self.unique_id + '.txt'))  ## replacing log with txt for UI compatibility
            LoggingConfig(os.path.join(self.log_dir, 'Suite_' + self.unique_id + '.txt'))  ## replacing log with txt for UI compatibility
            # LoggingConfig(suiteLogsLoc)
            logging.info("------suite logs------"+ str(suiteLogsLoc))
        
            current_testcase_data = self._getTestCaseData(data)
            if "TESTCASE_DATA" not in self._CONFIG:
                self._CONFIG["TESTCASE_DATA"] = current_testcase_data
            else:
            #     # Append the testcase data to the existing data
                self._CONFIG["TESTCASE_DATA"].update(current_testcase_data)
            self._CONFIG["SUITE_DATA"]['LOG_DIR'] = self.log_dir
            self._CONFIG["SUITE_DATA"]['UNIQUE_ID'] = self.unique_id

    def _getSuiteData(self, data) -> Dict:

        suite_data = data.find("suite")

        suite_dict = xmlToDict(suite_data)
        suite_dict={key.replace('-','_'):value for key,value in suite_dict.items()}
        suite_dict["SUITE_VARS"] = {}
        logging.info("suite_dict: \n {suite_dict} \n".format(suite_dict=suite_dict))
        # do your validations here

        return suite_dict

    def _getTestCaseData(self, data) -> Dict:

        testcase_data = data.find("testcases")

        testcase_list = xmlToList(testcase_data)

        for i in testcase_list:
            i["NAME"] = i["NAME"].upper()  ## uppercase

        testcase_list=[{key.replace('-','_'):value for key,value in testcase.items()} for testcase in testcase_list]

        testcase_dict = {k['NAME']: k for k in testcase_list}  #####################

        # do your validation here

        return testcase_dict
    
    def handleSpecialSymbols(self,filePath):
        filePath1=os.path.join(tempfile.gettempdir(),"temp.xml")
        f=open(filePath,"r")
        content=f.read()
        if(content.__contains__("&") and not(content.__contains__("&amp;"))):
            content=content.replace("&","&amp;")
        f1=open(filePath1,"w")
        f1.write(content)
        return filePath1
