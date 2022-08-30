from calendar import different_locale
from ctypes import util
import logging as logger
import json
import traceback
from numpy import isin
from gempyp.libs.enums.status import status
from gempyp.pyprest.utils import getKeyList 




class legacyApiComparison:
    def __init__(self,pyprest_obj):
        self.pyprest_obj = pyprest_obj
        self.legacy_api_response = self.pyprest_obj.__dict__["legacy_res"]
        self.current_api_response = self.pyprest_obj.__dict__["res_obj"]
        self.current_status_code = self.current_api_response.status_code
        self.legacy_status_code = self.legacy_api_response.status_code
        self.legacy_response_body = json.loads(self.legacy_api_response.response_body)
        self.current_response_body = json.loads(self.current_api_response.response_body)
        self.legacy_response_keys = getKeyList().getKeys(self.legacy_response_body)
        self.current_response_keys = getKeyList().getKeys(self.current_response_body)
        self.logger = self.pyprest_obj.logger
        self.reporter = self.pyprest_obj.reporter

    
    def compare_all(self):
        try:
            self.pyprest_obj.reporter.addRow("Executing Post Assertion check", "Running Assertion on legacy and current API Responses", status.INFO, CURRENT_API="Results | For Current API",LEGACY_API="Results | For Legacy API")
            if compareStatusCodes(self.legacy_status_code, self.current_status_code):
                title = "Comparing status codes of both the responses."
                description = "Both are Equal"
                _status = status.PASS
                legacy_desc = f"<b>LEGACY RESPONSE CODE:</b> {self.legacy_status_code}"
                current_desc = f"<b>CURRENT RESPONSE CODE:</b> {self.current_status_code}"
                self.reporter.addRow(title, description, _status, CURRENT_API=current_desc, LEGACY_API=legacy_desc)

                if compareTypeOfResponses(self.legacy_response_body, self.current_response_body):
                    title = "Comparing type of both the responses."
                    description = "Both responses are of same type"
                    _status = status.PASS
                    legacy_desc = f"<b>LEGACY RESPONSE TYPE:</b> {type(self.legacy_response_body).__name__}"
                    current_desc = f"<b>CURRENT RESPONSE TYPE:</b> {type(self.current_response_body).__name__}"
                    self.reporter.addRow(title, description, _status, CURRENT_API=current_desc, LEGACY_API=legacy_desc)
                   
                    if compareNumberOfKeys(self.legacy_response_keys, self.current_response_keys):
                        title = "Comparing Number of keys in responses"
                        description = "Both have equal number of keys"
                        _status = status.PASS
                        legacy_desc = f"<b>NUMBER OF KEYS IN LEGACY RESPONSE:</b> {len(self.legacy_response_keys)}"
                        current_desc = f"<b>NUMBER OF KEYS IN CURRENT RESPONSE:</b> {len(self.current_response_keys)}"
                        self.reporter.addRow(title, description, _status, CURRENT_API=current_desc, LEGACY_API=legacy_desc)
                        
                        if compareKeys(self.legacy_response_keys, self.current_response_keys):
                            title = "Comparing the set of keys in responses"
                            description = "Both responses have same set of keys"
                            _status = status.PASS
                            legacy_desc = f"<b>LIST OF KEYS IN LEGACY RESPONSE:</b>  {self.legacy_response_keys}"
                            current_desc = f"<b>LIST OF KEYS IN CURRENT RESPONSE:</b> {self.current_response_keys}"
                            self.reporter.addRow(title, description, _status, CURRENT_API=current_desc, LEGACY_API=legacy_desc)
                            
                            if isinstance(self.current_response_body,list) and isinstance(self.legacy_response_body,list):
                                
                                if len(self.current_response_body) == len(self.legacy_response_body):
                                    self.reporter.addRow("Comparing | Record Count of both responses", "Both responses have same count of records", status.PASS, CURRENT_API="Record Count: {}".format(len(self.current_response_body)), LEGACY_API="Record Count: {}".format(len(self.legacy_response_body)))
                                    
                                    for i in range(len(self.legacy_response_body)):
                                        compareResponses(self.reporter, self.current_response_body[i], self.legacy_response_body[i])                                        
                                
                                else:
                                    self.reporter.addRow("Comparing | Record Count of both responses", "Record Count MissMatch", status.FAIL, CURRENT_API="Record Count: {}".format(len(self.current_response_body)), LEGACY_API="Record Count: {}".format(len(self.legacy_response_body)))
                                    
                                    if "Record Count Missmatch, " not in self.reporter._misc_data["REASON_OF_FAILURE"]:  
                                        self.reporter._misc_data["REASON_OF_FAILURE"] += "Record Count Missmatch, "
                            
                            elif isinstance(self.current_response_body,dict) and isinstance(self.legacy_response_body,dict):
                                compareResponses(self.reporter, self.current_response_body, self.legacy_response_body)
                       
                        else:
                            title = "Comparing the number of keys in responses"
                            description = "Both responses do not have same set of keys"
                            _status = status.FAIL
                            legacy_desc = f"<b>LIST OF KEYS IN LEGACY RESPONSE:</b> {self.legacy_response_keys}"
                            current_desc = f"<b>LIST OF KEYS IN CURRENT RESPONSE:</b> {self.current_response_keys}"
                            self.reporter.addRow(title, description, _status, CURRENT_API=current_desc, LEGACY_API=legacy_desc)
                            
                            if "Set of keys do not match, " not in self.reporter._misc_data["REASON_OF_FAILURE"]:  
                                        self.reporter._misc_data["REASON_OF_FAILURE"] += "Set of keys do not match, "
                    
                    else:
                        title = "Comparing Count of keys in responses"
                        description = "Both do not have equal number of keys."
                        _status = status.FAIL
                        legacy_desc = f"<b>NUMBER OF KEYS IN LEGACY RESPONSE:</b> {len(self.legacy_response_keys)}"
                        current_desc = f"<b>NUMBER OF KEYS IN CURRENT RESPONSE:</b> {len(self.current_response_keys)}"
                        self.reporter.addRow(title, description, _status, CURRENT_API=current_desc, LEGACY_API=legacy_desc)
                        
                        if "Key Count MissMatch, " not in self.reporter._misc_data["REASON_OF_FAILURE"]:  
                                        self.reporter._misc_data["REASON_OF_FAILURE"] += "Key Count MissMatch, "

                else:
                    title = "Comparing type of both the responses."
                    description = "Both responses are not of same type"
                    _status = status.FAIL
                    legacy_desc = f"<b>LEGACY RESPONSE TYPE:</b> {type(self.legacy_response_body).__name__}"
                    current_desc = f"<b>CURRENT RESPONSE TYPE:</b> {type(self.current_response_body).__name__}"
                    self.logger.warning("---------- Missmatch in responses status codes. ")
                    self.reporter.addRow(title, description, _status, CURRENT_API=current_desc, LEGACY_API=legacy_desc)
                    
                    if "Response Type Missmatch, " not in self.reporter._misc_data["REASON_OF_FAILURE"]:  
                                        self.reporter._misc_data["REASON_OF_FAILURE"] += "Response Type Missmatch, "

            else:
                title = "Comparing status codes of both the responses."
                description = "Both are not Equal"
                _status = status.FAIL
                legacy_desc = f"<b>LEGACY RESPONSE CODE:  </b>{self.legacy_status_code}"
                current_desc = f"<b>CURRENT RESPONSE CODE: </b> {self.current_status_code}"
                self.reporter.addRow(title, description, _status, CURRENT_API=current_desc, LEGACY_API=legacy_desc)
                
                if "Response status code missmatch, " not in self.reporter._misc_data["REASON_OF_FAILURE"]:  
                                        self.reporter._misc_data["REASON_OF_FAILURE"] += "Response status code missmatch, "
                self.logger.warning("---------- Missmatch in responses status codes. ")

        except Exception as e:
            self.logger.info(traceback.print_exc())
            self.reporter._misc_data["REASON_OF_FAILURE"] += f"Some error occurred while sending request- {str(e)}, "
            raise Exception("Error occured while sending request - {0}".format(str(e)))



def compareResponses(reporter, current_response, legacy_response):
    if len(current_response)>0 and len(legacy_response)>0:
        
        for (legacy_key, legacy_value), (current_key, current_value) in zip(legacy_response.items(), current_response.items()):
        
            if isinstance(legacy_value, str) and isinstance(current_value, str): 
                responseReporter(reporter, legacy_key, current_key, legacy_value, current_value)
        
            elif isinstance(legacy_value,int) or isinstance(current_value,int):
                responseReporter(reporter, legacy_key, current_key, legacy_value, current_value)                                     
        
            elif isinstance(legacy_value,float) or isinstance(current_value,float):
                responseReporter(reporter, legacy_key, current_key, legacy_value, current_value) 
        
            elif isinstance(legacy_value,bool) or isinstance(current_value,bool):
                responseReporter(reporter, legacy_key, current_key, legacy_value, current_value)
            
            # elif isinstance(legacy_value,None) or isinstance(current_value,None):  #yet to handle 

            elif isinstance(legacy_value, list) or isinstance(current_response,list):
                listComparator(reporter,legacy_key, current_key, legacy_value, current_value)
        
            elif isinstance(legacy_value,dict) or isinstance(current_value,dict):
                compareResponses(reporter, current_value, legacy_value)


def listComparator(reporter,legacy_key, current_key, legacy_value, current_value):
    title = ""
    description = ""
    _status = ""
    current_info = ""
    legacy_info = ""
    if legacy_key == current_key:
        title = f"Comparing | <b>{legacy_key}</b> for Legacy & Current API"
        current_info = f"value = {legacy_value}"
        legacy_info = f"Value = {current_value}"
        if len(legacy_value) != len(current_value) and len(legacy_value)>0 and len(current_value)>0:
            title = "Comparing | record count of <b>{}</b> for legacy and current API".format(legacy_key)
            description = "Record count is not equal"
            _status = status.FAIL
            reporter.addRow(title,description,_status,CURRENT_API=len(current_value), LEGACY_API=len(legacy_value))
            if "Record count not equal, " not in reporter._misc_data["REASON_OF_FAILURE"]:  
                    reporter._misc_data["REASON_OF_FAILURE"] += "Record count not equal, "
        elif len(legacy_value) == len(current_value) and len(legacy_value)>0 and len(current_value)>0:
            title = "Comparing | record count of <b>{}</b> for legacy and current API".format(legacy_key)
            description = "Record count is equal"
            _status = status.PASS
            reporter.addRow(title,description,_status,CURRENT_API=len(current_value), LEGACY_API=len(legacy_value))
            if legacy_value == current_value:
                title = f"Comparing | list of <b>{legacy_key}</b> for Legacy & Current API"
                description = "Values are equal"
                _status = status.PASS
                reporter.addRow(title,description,_status,CURRENT_API=current_info, LEGACY_API=legacy_info)
            else:
                title = f"Comparing | list of <b>{legacy_key}</b> for Legacy & Current API"
                description = "Values are not equal"
                _status = status.FAIL
                reporter.addRow(title,description,_status,CURRENT_API=current_info, LEGACY_API=legacy_info)
                if "Mismatches found during Assertion, " not in reporter._misc_data["REASON_OF_FAILURE"]:  
                    reporter._misc_data["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "
        elif len(legacy_value)==0 and len(current_value)==0:
            title = f"Comparing | list of <b>{legacy_key}</b> for Legacy & Current API"
            description = "Empty List"
            _status = status.PASS
            reporter.addRow(title,description,_status,CURRENT_API="[ ]", LEGACY_API="[ ]")
            

def responseReporter(reporter, legacy_key, current_key, legacy_value, current_value):
    title = ""
    description = ""
    _status = ""
    current_info = ""
    legacy_info = ""
    if legacy_key == current_key:
        title = f"Comparing | <b>{legacy_key}</b> for Legacy & Current API"
        current_info = f"value = {legacy_value}"
        legacy_info = f"Value = {current_value}"
        if legacy_value == current_value:
            description = f"Values are Equal"
            _status = status.PASS
            reporter.addRow(title, description, _status, CURRENT_API=current_info, LEGACY_API=legacy_info)
        else:
            description = f"Values are not Equal"
            _status = status.FAIL
            reporter.addRow(title, description, _status, CURRENT_API=current_info, LEGACY_API=legacy_info)
            if "Mismatches found during Assertion, " not in reporter._misc_data["REASON_OF_FAILURE"]:  
                    reporter._misc_data["REASON_OF_FAILURE"] += "Mismatches found during Assertion, "


def compareTypeOfResponses(legacy_response, current_response):
    logger.info("+++++++++++++++++++++ COMPARING TYPES OF RESPONSES +++++++++++++++++++++")
    if type(legacy_response) is type(current_response):
        logger.warning("+++++++++++++++++++++ TYPE MATCHED +++++++++++++++++++++")
        logger.info("+++++++++++++++++++++ Type of Legacy Response - {}".format(type(legacy_response).__name__))
        logger.info("+++++++++++++++++++++ Type of Current Response - {}".format(type(current_response).__name__))
        return True
    else:
        logger.warning("+++++++++++++++++++++ TYPE MISMATCHED +++++++++++++++++++++")
        logger.info("+++++++++++++++++++++ Type of Legacy Response - {}".format(type(legacy_response).__name__))
        logger.info("+++++++++++++++++++++ Type of Current Response - {}".format(type(current_response).__name__))
        return False


def compareNumberOfKeys(legacy_response_keys, current_response_keys):
    logger.info("+++++++++++++++++++++ COMPARING NUMBER OF KEYS OF RESPONSES +++++++++++++++++++++")
    if len(legacy_response_keys) == len(current_response_keys):
        logger.warning("+++++++++++++++++++++ Both responses have equal number of keys +++++++++++++++++++++")
        return True
    else:
        logger.warning("+++++++++++++++++++++ Both responses not have equal number of keys +++++++++++++++++++++")
        return False


def compareKeys(legacy_response_keys, current_response_keys):
    if legacy_response_keys == current_response_keys:
        logger.warning("+++++++++++++++++++++ Both responses have same keys +++++++++++++++++++++")
        return True
    else:
        logger.warning("+++++++++++++++++++++ Both responses do not have same keys +++++++++++++++++++++")
        return False


def compareStatusCodes(legacy_status_code, current_status_code):
    logger.info("+++++++++++++++++++++ COMPARING THE STATUS CODES OF RESPONSES +++++++++++++++++++++")
    if legacy_status_code == current_status_code:
        logger.warning("status codes are same %s, %s ",legacy_status_code, current_status_code)
        return True
    else:
        logger.warning("status codes are different %s, %s ",legacy_status_code, current_status_code)
        return False