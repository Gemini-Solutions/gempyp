import logging as logger
import gempyp.pyprest.compareFunctions as cf
from gempyp.pyprest.keyCheck import KeyCheck
from gempyp.pyprest import utils
from gempyp.pyprest.utils import getKeyList
from copy import deepcopy
from gempyp.pyprest.legacyComparison import legacyApiComparison
from gempyp.libs.enums.status import status
from gempyp.pyprest.variableReplacement import VariableReplacement as var_replacement


class PostAssertion:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        self.logger = self.pyprest_obj.logger
        self.isLegacyPresent = False
        self.legacy_all_keys = []
        self.all_keys = []
        self.notCompareAll = True
        self.space_handler = {
            "not to": "notto",
            "not in": "notin",
        }
        pass

    def postAssertion(self):
        """This function-
        -parses post assertion string and runs keycheck on the keys for post assertion
        -for the keys that are found in the response, fetches their values
        -gets the comparison result and update logs and reporter obj.
        """
        if self.pyprest_obj.post_assertion:
            self.logger.info("************** INSIDE POST ASSERTION  **************") 
            var_replacement(self.pyprest_obj).variableReplacement()

            #
            if self.pyprest_obj.legacy_res is not None:
                self.logger.info("Legacy API found, proceeding for post assertion accordingly....")
                self.isLegacyPresent = True
                self.legacy_all_keys = getKeyList().getKeys(utils.formatRespBody(self.pyprest_obj.legacy_res.response_body))
                self.all_keys = getKeyList().getKeys(utils.formatRespBody(self.pyprest_obj.res_obj.response_body))
            self.post_assertion_str = " ".join(self.pyprest_obj.post_assertion.split())
            
            if 'COMPARE ALL' in self.post_assertion_str.upper():
                self.notCompareAll = False

            post_ass_str_list = self.post_assertion_str.strip(";").split(";")
            
            key_str = []
            legacy_key_str = []
            # comparison_val_str = []

            assertion_list = self.getAssertionDict(post_ass_str_list)
            for each in assertion_list:
                if 'legacy' in list(each.keys())[0]:
                    legacy_key_str.append(list(each.keys())[0])
                elif list(each.keys())[0].upper() == 'ALL':
                    legacyApiComparison(self.pyprest_obj).compare_all()
                else:
                    key_str.append(list(each.keys())[0])
            key_str = list(set(key_str))
            if len(legacy_key_str)>0:
                 legacy_key_str = list(set(legacy_key_str))
            
            
            if self.isLegacyPresent and len(self.all_keys)==0 and self.notCompareAll:
                self.pyprest_obj.reporter.addRow("Executing Post Assertion check", "Keys for assertion check", status.INFO, CURRENT_API="Keys to execute assertion check in current API are: " + "".join(key_str),LEGACY_API="Keys to execute assertion check in legacy API are: " + "".join(legacy_key_str))
            elif self.isLegacyPresent and len(self.all_keys) > 0 and self.notCompareAll:
                self.pyprest_obj.reporter.addRow("Executing Post Assertion check", "Running Assertion on legacy and current API Responses", status.INFO, CURRENT_API="Assertions for Current API",LEGACY_API="Assertions for Legacy API")
            elif self.notCompareAll:
                self.pyprest_obj.reporter.addRow("Executing Post Assertion check", "Keys to execute assetion check are: " + "".join(key_str), status.INFO)

            self.logger.info("Post assertion string- " + self.post_assertion_str)
            
            
            
            list_of_all_keys = [*list(set(key_str)) , *list(set(legacy_key_str))]
            key_val_dict = {}              
            for each_assert in list_of_all_keys:
                key_part_list = each_assert.split(".") 
                if "legacy" in each_assert:
                    response_json = utils.formatRespBody(self.pyprest_obj.legacy_res.response_body)
                else:
                    response_json = utils.formatRespBody(self.pyprest_obj.res_obj.response_body)
                result = KeyCheck(self.pyprest_obj).findKeys(response_json, deepcopy(key_part_list), deepcopy(key_part_list))
                if result.upper() != "FOUND":
                    self.logger.info("====== Key Not Found in response =======")
                    self.logger.info("'" + each_assert + "' is not found")
                    if self.isLegacyPresent and "legacy" in each_assert:
                        self.pyprest_obj.reporter.addRow("Executing post assertion on current API ", f"Checking presence of key {each_assert} in response", status.FAIL, CURRENT_API="-",LEGACY_API=f"Key {each_assert} is not found in the response")
                        self.pyprest_obj.reporter.addMisc("REASON OF FAILURE", "Some keys are missing in Response")
                    else:    
                        self.pyprest_obj.reporter.addRow(f"Checking presence of key {each_assert} in response", f"Key {each_assert} is not found in the response", status.FAIL)
                        self.pyprest_obj.reporter.addMisc("REASON OF FAILURE", "Some keys are missing in Response")
                else:
                    key_val_dict = utils.fetchValueOfKey(response_json, key_part_list, result, key_val_dict)
            self.postAssertionFunc(key_val_dict, assertion_list)

    def getAssertionDict(self, string_list):     
        """assertion list-
        [
            {keys: {operator: operator, value: expected value}},
        ]
        """
        # need to add condition for compare all and compare all except in legacy
        temp_str = str(";".join(string_list))
        for i in self.space_handler.keys():
            temp_str = temp_str.replace(str(i), self.space_handler[i])
        string_list = temp_str.split(';')
        flag = 0
        list_ = []
        for each in string_list:
            if "COMPARE" == each.strip(" ").split(" ")[0].upper():
                each = each.strip(" ").split(" ", 1)[1]
                flag = 1
            if flag == 1:
                assert_str = each.strip(" ").split(" ", 1)
                key = assert_str[0]
                opr_val = assert_str[1].strip(" ").split(" ", 1)
                opr = opr_val[0].strip(" ")
                val = opr_val[1].strip(" ")
                list_.append(dict({key: {"operator": "".join(opr.strip(" ")), "value": val.strip(" ")}}))
        return list_

    def postAssertionFunc(self, key_val_dict, assertion_list):
        """This function-
        -removes the element from the assertion dict that are not valid
        -calls comparison functions based on the operator type
        """
        self.logger.info("-----------inside assertion func-----------")

        # removing the keys that are not present
        for ele in assertion_list:
            if list(ele.keys())[0] not in key_val_dict.keys():
                assertion_list.remove(ele)
        key_val_dict_legacy = {}
        # calling compare function for each validation string
        for each_assert in assertion_list:
            result_legacy = ''
            key = list(each_assert.keys())[0]
            operator = list(each_assert.values())[0]['operator']
            value = list(each_assert.values())[0]['value']            
            if self.isLegacyPresent and value.split(".")[-1] in self.legacy_all_keys or value.split(".")[-1] in self.all_keys and '"' not in value and "'" not in value: 
                key_part_list = value.split(".") 
                if 'legacy' in value:
                    result_legacy = KeyCheck(self.pyprest_obj).findKeys(utils.formatRespBody(self.pyprest_obj.legacy_res.response_body), deepcopy(key_part_list), deepcopy(key_part_list))
                    if result_legacy == 'FOUND':
                        key_val_dict_legacy = utils.fetchValueOfKey(utils.formatRespBody(self.pyprest_obj.legacy_res.response_body), key_part_list, result_legacy, key_val_dict_legacy)
                else:
                    result_legacy = KeyCheck(self.pyprest_obj).findKeys(utils.formatRespBody(self.pyprest_obj.res_obj.response_body), deepcopy(key_part_list), deepcopy(key_part_list))
                    if result_legacy == 'FOUND':
                        key_val_dict_legacy = utils.fetchValueOfKey(utils.formatRespBody(self.pyprest_obj.res_obj.response_body), key_part_list, result_legacy, key_val_dict_legacy)              
                                
            elif self.isLegacyPresent and not value.isdigit() and  '"' not in value and "'" not in value:
                if 'legacy' in value :
                    self.pyprest_obj.reporter.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"Key not found",status.FAIL, CURRENT_API=f"-", LEGACY_API=f"{value} key missing in legacy response")  
                else:
                    self.pyprest_obj.reporter.addRow(f"Running Assertion on comparing the respective values of {key} and {value}",f"Key not found",status.FAIL, CURRENT_API=f"{value} key missing in Current response", LEGACY_API=f"-")
                    self.pyprest_obj.reporter.addMisc("REASON OF FAILURE", "key for comparison not found in response")

            tolerance = 0.1
            if result_legacy == "FOUND":
                if operator == "notto":
                    cf.compare_notto_resp(self.pyprest_obj.reporter,key, value, key_val_dict, key_val_dict_legacy, result_legacy,tolerance)
                elif operator == "to" :
                    cf.compareToResp(self.pyprest_obj.reporter,key,value,key_val_dict,key_val_dict_legacy, result_legacy, tolerance)
            elif (value.split(".")[-1] not in self.all_keys) and ('legacy' in key and self.isLegacyPresent and len(key_val_dict_legacy)==0):
                self.pyprest_obj.reporter = utils.compare(self.pyprest_obj.reporter, key, operator, value, key_val_dict, tolerance,self.isLegacyPresent, True)
            elif (value.split(".")[-1]) not in self.legacy_all_keys and 'legacy' not in key and self.isLegacyPresent and len(key_val_dict_legacy)==0:
                self.pyprest_obj.reporter = utils.compare(self.pyprest_obj.reporter, key, operator, value, key_val_dict, tolerance, self.isLegacyPresent)
            elif not self.isLegacyPresent:
                self.pyprest_obj.reporter = utils.compare(self.pyprest_obj.reporter, key, operator, value, key_val_dict, tolerance)
                            

                

