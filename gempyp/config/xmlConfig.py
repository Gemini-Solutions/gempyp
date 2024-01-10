import tempfile
import traceback
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


    def parse(self, filePath):

        logging.info("-------- Xml file path: {filePath} ----------".format(filePath=filePath))
        path_list = filePath.split(os.sep)[0:-1]
        newfilePath = os.sep.join(path_list)
        sys.path.append({"XMLConfigDir":newfilePath})
        logging.info("-------- Started the Xml parsing in XmlConfig ---------")
        filePath=self.handleSpecialSymbols(filePath)
        # data = et.parse(filePath)
        parser = CustomXMLParser(remove_comments=True)
        data = etree.parse(filePath, parser=parser)
        self._CONFIG["SUITE_DATA"] = self._getSuiteData(data) 
        #code for replacing variable from external properties file
        external_file_variables = None
        if "PROPERTIES_FILE" in self._CONFIG["SUITE_DATA"]:
            try:
                external_file_variables = self.read_variable_from_file(self._CONFIG["SUITE_DATA"]["PROPERTIES_FILE"])
                if self._CONFIG["SUITE_DATA"].get("PROPERTIES_FILE"):
                        self._CONFIG["SUITE_DATA"] = self.replace_variables_from_file(external_file_variables,self._CONFIG["SUITE_DATA"])
            except Exception as e:
                    logging.info(traceback.print_exc())
                    print("Some error ocurred during variable replacement. Please check variables from external file")
                    sys.exit()
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
        logging.info("suite logs : "+ str(suiteLogsLoc))
        self._CONFIG["TESTCASE_DATA"] = self._getTestCaseData(data)
        if self._CONFIG["SUITE_DATA"].get("PROPERTIES_FILE") and external_file_variables:
            self.replace_variables_for_testcase(external_file_variables, self._CONFIG["TESTCASE_DATA"])
        self._CONFIG["SUITE_DATA"]['LOG_DIR'] = self.log_dir
        self._CONFIG["SUITE_DATA"]['UNIQUE_ID'] = self.unique_id
        return suiteLogsLoc

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
    
    def replace_substring(self,original_string, start_index, end_index, replacement):
        # Construct the modified string by concatenating the substring before and after the replacement
        modified_string = original_string[:start_index] + replacement + original_string[end_index + 1:]
        return modified_string

    def find_end_index_array(self,ch,string1)->list:
        """
        return list of indexes
        """
        pos= []
        for i in range(len(string1)):
            if ch == string1[i]:
                pos.append(i)
        return pos
    
    def read_variable_from_file(self, file_path)->Dict:
        print("Reading external file")
        files = file_path.split(',')
        final_variable_dict = {}
        for file in files:
            if os.path.exists(file):
                with open(file) as f:
                    l = [line.split("=") for line in f.readlines()]
                    d = {key.strip(): value.strip() for key, value in l}
                final_variable_dict = {**final_variable_dict, **d}
            else:
                print(f"File given in external files not found:{file}")
                sys.exit()
        return {key: (int(value) if value.isdigit() else float(value)) if value.replace('.', '', 1).isdigit() else value for key, value in final_variable_dict.items()}
        
    
    def replace_variables_from_file(self,variable_dict, suite_dict):
        print("In variable replacement")
        values_with_variables = [[key,val] for key, val in suite_dict.items() if "$[#EXTERNAL." in val]
        for i in values_with_variables:
            string = i[1]
            start_indexes = [i for i in range(len(string)) if string.startswith("$[#EXTERNAL.", i)]
            for start_index in start_indexes:
                start_index = string.index("$[#EXTERNAL.")
                end_index = self.find_end_index_array("]",string)
                closest_value = min([i for i in end_index if i-start_index > 0])
                variable_name = string[start_index+12:closest_value]
                variable_value = variable_dict.get(variable_name,None)
                if variable_value == None:
                    print(f"Value for variable '{variable_name}' not found")
                    sys.exit()
                if variable_value:
                    string = self.replace_substring(string, start_index,closest_value,variable_value)
            suite_dict[i[0]]= string
        return suite_dict


    def replace_variables_for_testcase(self,variable_dict,testcase_dict):
        try:
            for key,value in testcase_dict.items():
                self._CONFIG["TESTCASE_DATA"][key] = self.replace_variables_from_file(variable_dict,value)
        except Exception as e:
            logging.info(traceback.print_exc())



