import logging as logger
from gempyp.pyprest.keyCheck import KeyCheck
from gempyp.pyprest import utils
from copy import deepcopy
from gempyp.libs.enums.status import status
from gempyp.pyprest.variableReplacement import VariableReplacement as var_replacement


class PostAssertion:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        pass

    def postAssertion(self):
        """This function-
        -parses post assertion string and runs keycheck on the keys for post assertion
        -for the keys that are found in the response, fetches their values
        -gets the comparison result and update logs and reporter obj.
        """
        if self.pyprest_obj.post_assertion:
            logger.info("++++++++++++++++++++++++++++++++++++++  INSIDE POST ASSERTION  ++++++++++++++++++++++++++++++++++++++")
            var_replacement(self.pyprest_obj).variableReplacement()
            self.post_assertion_str = self.pyprest_obj.post_assertion
            post_ass_str_list = self.post_assertion_str.strip(";").split(";")
            key_str = []
            for each in post_ass_str_list:
                key_str.append(str(list(str(each).split(" "))[1]))
            assertion_list = self.getAssertionDict(post_ass_str_list)  # list of dictionaries of operator and values for keys
            # get a string of comma separated keys

            self.pyprest_obj.reporter.addRow("Executing Post Assertion check", "Keys to execute assetion check are: </br>" + "</br>".join(key_str), status.INFO)

            logger.info("Post assertion string- " + self.post_assertion_str)
            key_val_dict = {}
            for each_assert in list(set(key_str)):
                key_part_list = each_assert.split(".")
                response_json = utils.formatRespBody(self.pyprest_obj.res_obj.response_body)
                result = KeyCheck(self.pyprest_obj).findKeys(response_json, deepcopy(key_part_list), deepcopy(key_part_list))
                if result.upper() != "FOUND":
                    logger.info("====== Key Not Found in response =======")
                    logger.info("'" + each_assert + "' is not found")
                    self.pyprest_obj.reporter.addRow(f"Checking presence of key {each_assert} in response", f"Key {each_assert} is not found in the response", status.FAIL)
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
        list_ = []
        for each in string_list:
            items = each.split(" ")
            if '[' in each:
                br_start = each.rfind('[')
                br_end = each.rfind(']')
                if each[br_start - 1] in ["'", '"', "$", " "]:
                    items = each[:br_start - 1].split(" ") + [each[br_start:br_end + 1]] + each[br_end + 1:].split(" ")
                if "" in items:
                    items.remove("")
            if items[0].strip(" ").upper() == "COMPARE":
                list_.append(dict({items[1]: {"operator": "".join(items[2:-1]), "value": items[-1]}}))
        return list_

    def postAssertionFunc(self, key_val_dict, assertion_list):
        """This function-
        -removes the element from the assertion dict that are not valid
        -calls comparison functions based on the operator type
        """
        logger.info("-----------inside assertion func----------------------------")

        # removing the keys that are not present
        for ele in assertion_list:
            if list(ele.keys())[0] not in key_val_dict.keys():
                assertion_list.remove(ele)

        # calling compare function for each validation string
        for each_assert in assertion_list:
            key = list(each_assert.keys())[0]
            operator = list(each_assert.values())[0]['operator']
            value = list(each_assert.values())[0]['value']
            tolerance = 0.1
            self.pyprest_obj.reporter = utils.compare(self.pyprest_obj.reporter, key, operator, value, key_val_dict, tolerance)
