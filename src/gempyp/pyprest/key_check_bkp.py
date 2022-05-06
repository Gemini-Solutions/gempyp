import ast
import json
import re
from pygem.libs.enums.status import status
import traceback


class key_check:
    def __init__(self, pirest_obj):
        self.pirest_obj = pirest_obj
        pass

    def key_check(self):
        self.response_body = {}
        if self.pirest_obj.key_check and "keys are" in self.pirest_obj.key_check:
            self.pirest_obj.key_check = self.pirest_obj.key_check
            print("keycheck string: " + str(self.pirest_obj.key_check))
            type_list = self.pirest_obj.key_check.strip(";").split(";")
            self.keys = []
            self.keys_not = []
            for each in type_list:

                # not condition
                if "keys are not" in each:
                    key_not_str = each.split("keys are not")
                    self.keys_not = [i.strip(" ") for i in key_not_str.split(",")]

                # keys are condition 
                if "keys are" in each:
                    key_str = each.split("keys are")[1]
                    keys = [i.strip(" ") for i in key_str.split(",")]
                    self.keys = list(set(keys) - set(self.keys_not))


                if not isinstance(self.pirest_obj.res_obj.response_body, list):
                    try:
                        self.response_body = json.loads(self.pirest_obj.res_obj.response_body.decode("utf-8"))
                        print("keycheck ----- 1")
                    except Exception:
                        try:
                            self.response_body = json.loads(ast.literal_eval(self.pirest_obj.res_obj.response_body.decode("utf-8")))
                            print("keycheck ----- 2")
                        except Exception:
                            try: 
                                self.response_body = json.loads(str(self.pirest_obj.res_obj.response_body.encode("utf-8")))
                                if "b'" in self.response_body:
                                    self.response_body = self.response_body.strip("b'").strip("'")
                                print("keycheck ----- 3")
                            except Exception:
                                try:
                                    self.response_body = json.loads(self.pirest_obj.res_obj.response_body)
                                except Exception as e:
                                    self.response_body = self.pirest_obj.res_obj.response_body

                else:
                    self.response_body = self.pirest_obj.res_obj.response_body
                self.regex_each = re.compile(r".*\[\beach\b\]")
                self.regex_int = re.compile(r".*\[\d+\]")

                self.get_keys()

        else:
            print("keycheck not performed----------------------")

    def get_keys(self):
        count_found_fail, count_notfound_fail = 0, 0
        _status, _status_n = status.INFO, status.INFO
        content_found = ""  # html content, add all the key checks in single row
        content_not_found = ""
        if len(self.keys) > 0:
            for each_key in self.keys:
                self.key_list = [str(i) for i in each_key.split(".")]
                self.temp_key_list = list(self.key_list)
                result = self.find_keys(self.response_body, self.key_list)
                if "NOT FOUND" in result:
                    count_found_fail += 1
                content_found += "<b>" + ".".join(self.key_list) + "</b>=" + result + "<br>"

                if count_found_fail > 0:
                    _status = status.FAIL
                else:
                    _status = status.PASS
            self.pirest_obj.reporter.addRow("Keys to be check for PRESENCE in response body", content_found, _status)
        if len(self.keys_not) > 0:
            for each_key in self.keys_not:
                self.key_list = [str(i) for i in each_key.split(".")]
                self.temp_key_list = list(self.key_list)
                result = self.find_keys(self.response_body, self.key_list)
                if result == "FOUND":
                    count_notfound_fail += 1
                content_not_found += "<b>" + ".".join(self.key_list) + "</b>=" + result + "<br>"

                if count_notfound_fail > 0:
                    _status_n = status.FAIL
                else:
                    _status_n = status.PASS
            self.pirest_obj.reporter.addRow("Keys not required in response body", content_not_found, _status_n)

        if status.FAIL in [_status, _status_n]:
            self.pirest_obj.reporter._miscData["Reason_of_failure"] = "Status of key check is not as expected"
            # self.pirest_obj.reporter.addMisc(Reason_of_failure="Status of key check is not as expected")


    def find_keys(self, json_data, key_list):
        print("===================FINDING KEYS=====================")
        for each in key_list:
            print(each, "----------------------------------------------------------------------")

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
                    return self.find_keys(json_data, key_list)

                # for data[each].something
                elif key_val in json_data and isinstance(json_data[key_val], list):
                    key_list.remove(each)
                    return self.find_keys(json_data[key_val], key_list)

                # return "NOT FOUND" if  key from string "key[each]" is not found in the json_data
                else:
                    print("Key not found ------------")
                    return "NOT FOUND"

            # for list like keychecks
            # example  response[0].data, data[0].color etc

            elif re.match(self.regex_int, each):
                br_start = each.find('[')
                br_end = each.find(']')
                key_val = each[:br_start]
                key_num = int(each[br_start + 1:br_end])

                # for response[0].something
                if key_val == "response" and isinstance(json_data, list) and key_num < len(json_data):
                    key_list.remove(each)
                    return self.find_keys(json_data[key_num], key_list)

                # for something like data[0].something
                elif key_val in json_data and isinstance(json_data[key_val], list) and key_num < len(json_data[key_val]):
                    key_list.remove(each)
                    return self.find_keys(json_data[key_val][key_num], key_list)
                else:
                    print("Key not found ------------")
                    return "NOT FOUND"

            # for simple keychecks ( list and dicts) or last steps of list and "each" parsing
            else:

                # if input is list
                if isinstance(json_data, list):
                    temp_list = list(key_list)
                    # self.temp_key_list has to be defined in get_keys
                    i = self.temp_key_list.index(temp_list[0])
                    count_not_found = 0

                    # check if the parent key of this key_to_ckeck contained each or not, because other cases are already covered 
                    # example data[each].key_to_find
                    if json_data and re.match(self.regex_each, self.temp_key_list[i - 1]):
                        for name in json_data:
                            if isinstance(name, dict):
                                found_res = self.find_keys(name, temp_list)
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
                        return self.find_keys(json_data[each], tmp_key)

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
