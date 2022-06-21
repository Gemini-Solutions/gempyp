import re
from gempyp.libs.enums.status import status
from gempyp.pyprest import utils
import logging as logging


class KeyCheck:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        self.regex_each = re.compile(r".*\[\beach\b\]")
        self.regex_int = re.compile(r".*\[\d+\]")
        pass

    def keyCheck(self):
        """
        Checks whether a key is present in the response or not.
        """
        self.pyprest_obj.logger.info("**************  INSIDE KEY CHECK  **************")

        self.response_body = {}
        if self.pyprest_obj.key_check and "keys are" in self.pyprest_obj.key_check.lower():
            self.pyprest_obj.key_check = self.pyprest_obj.key_check
            self.pyprest_obj.logger.info("keycheck string: " + str(self.pyprest_obj.key_check))
            type_list = self.pyprest_obj.key_check.strip(";").split(";")
            self.keys = []
            self.keys_not = []
            for each in type_list:

                # not condition
                if "keys are not" in each.lower():
                    key_not_str = each.split("keys are not")
                    self.keys_not = [i.strip(" ") for i in key_not_str.split(",")]

                # keys are condition 
                elif "keys are" in each.lower():
                    key_str = each.split("keys are")[1]
                    keys = [i.strip(" ") for i in key_str.split(",")]
                    self.keys = list(set(keys) - set(self.keys_not))

                self.response_body = utils.formatRespBody(self.pyprest_obj.res_obj.response_body)

                self.getKeys()

        else:
            self.pyprest_obj.logger.info("keycheck not performed----------------------")

    def getKeys(self):
        """
        Logging on the basis or presence or absence of keys"""
        count_found_fail, count_notfound_fail = 0, 0
        _status, _status_n = status.INFO, status.INFO
        content_found = ""  # html content, add all the key checks in single row
        content_not_found = ""
        if len(self.keys) > 0:
            for each_key in self.keys:
                self.key_list = [str(i) for i in each_key.split(".")]
                self.temp_key_list = list(self.key_list)
                result = self.findKeys(self.response_body, self.key_list, self.temp_key_list)
                if "NOT FOUND" in result:
                    count_found_fail += 1
                content_found += "<b>" + ".".join(self.key_list) + "</b>=" + result + "<br>"

                if count_found_fail > 0:
                    _status = status.FAIL
                else:
                    _status = status.PASS
            self.pyprest_obj.reporter.addRow("Keys to be check for PRESENCE in response body", content_found, _status)
        if len(self.keys_not) > 0:
            for each_key in self.keys_not:
                self.key_list = [str(i) for i in each_key.split(".")]
                self.temp_key_list = list(self.key_list)
                result = self.findKeys(self.response_body, self.key_list, self.temp_key_list)
                if result == "FOUND":
                    count_notfound_fail += 1
                content_not_found += "<b>" + ".".join(self.key_list) + "</b>=" + result + "<br>"

                if count_notfound_fail > 0:
                    _status_n = status.FAIL
                else:
                    _status_n = status.PASS
            self.pyprest_obj.reporter.addRow("Keys not required in response body", content_not_found, _status_n)

        if status.FAIL in [_status, _status_n]:
            self.pyprest_obj.reporter._miscData["Reason_of_failure"] = "Status of key check is not as expected"
            # self.pyprest_obj.reporter.addMisc(Reason_of_failure="Status of key check is not as expected")


    def findKeys(self, json_data, key_list, temp_key_list):
        """
        Finding keys in the response on the basis of the regex they match with
        """
        for each in key_list:
            self.pyprest_obj.logger.info(f"========FINDING KEY - {each}  ==========")
            """
            note : - if key to find is like data[0].color[9].code or something like data[each].color[9].code or any lind of nesting, then there will be recursion 
            and everytime the value after "." will be passed to the same function 
            i.e. first recusion --- for data[0]
                 second ----------- for color[9]
                 third ------------ for code
            """

            # parsing the keychecks with "each" in them
            if re.match(self.regex_each, each):
                br_index = each.find('[')
                key_val = each[:br_index]

                # for response[each].something
                if key_val == "response" and isinstance(json_data, list):
                    key_list.remove(each)
                    return self.findKeys(json_data, key_list, temp_key_list)

                # for data[each].something
                elif key_val in json_data and isinstance(json_data[key_val], list):
                    key_list.remove(each)
                    return self.findKeys(json_data[key_val], key_list, temp_key_list)

                # return "NOT FOUND" if  key from string "key[each]" is not found in the json_data
                else:
                    self.pyprest_obj.logger.info(f"{each}  - Key not found ------------")
                    return "NOT FOUND"

            # for list like keychecks
            # example  response[0].data, data[0].color etc

            elif re.match(self.regex_int, each):
                br_start = each.find('[')
                br_end = each.find(']')
                key_val = each[:br_start]
                key_num = int(each[br_start + 1:br_end])
                key_num, json_data = utils.getNestedListData(each, json_data, key_val)

                # for response[0].something
                if key_val == "response" and isinstance(json_data, list) and key_num < len(json_data):
                    key_list.remove(each)
                    return self.findKeys(json_data[key_num], key_list, temp_key_list)

                # for something like data[0].something
                elif key_val in json_data and isinstance(json_data[key_val], list) and key_num < len(json_data[key_val]):
                    key_list.remove(each)
                    return self.findKeys(json_data[key_val][key_num], key_list, temp_key_list)
                else:
                    self.pyprest_obj.logger.info(f"{each}  - Key not found ------------")
                    return "NOT FOUND"

            # for simple keychecks ( list and dicts) or last steps of list and "each" parsing
            else:

                # if input is list
                if isinstance(json_data, list):
                    temp_list = list(key_list)
                    i = temp_key_list.index(temp_list[0])
                    count_not_found = 0

                    # check if the parent key of this key_to_ckeck contained each or not, because other cases are already covered 
                    # example data[each].key_to_find
                    if json_data and re.match(self.regex_each, temp_key_list[i - 1]):
                        for name in json_data:
                            if isinstance(name, dict):
                                found_res = self.findKeys(name, temp_list, temp_key_list)
                                if found_res != "FOUND":
                                    count_not_found += 1
                            else:
                                return "NOT FOUND"
                        if count_not_found == 0:
                            return "FOUND"
                        else:

                            # return NOT FOUND if key not found in some_key[each][index]
                            return f"NOT FOUND, KEY MISSING IN {count_not_found} Items" # missing in number of objects( in case of each)

                    # return NOT FOUND if parent of key is not like some_key[each][index], because other scenarios of list are already covered
                    else:
                        return "NOT FOUND"

                # if input is dict
                elif isinstance(json_data, dict):
                    if each in json_data:
                        tmp_key = list(key_list)
                        tmp_key.remove(each)
                        if len(tmp_key) == 0:
                            return "FOUND"
                        return self.findKeys(json_data[each], tmp_key, temp_key_list)

                    # return not found if key not found in the dictionary i.e. the json_data . 
                    # json_data here is the json/list passed to this function in this recursion
                    else:
                        return "NOT FOUND"
                
                # return "NOT FOUND" if key doen not fall in any of the categories/conditions i.e. response[each] or some_key[each] or response[index] or some_key[index] or direct dictionary.key dict or li
                else:
                    return "NOT FOUND"

        # if the key w
        # as not found, then "NOT FOUND" must have been returned in any of the above conditions
        return "FOUND"
