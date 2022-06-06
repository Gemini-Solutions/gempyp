from gempyp.pyprest.key_check import key_check
from gempyp.pyprest import utils
from copy import deepcopy
import logging as logger
from gempyp.pyprest.variable_replacement import variable_replacement as var_replacement


class post_variables:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        # get variable written in data["POST_VARIABLE"]
        # postdefined func
        # remove $[#]
        # assign_values and append to a dict
        # different dicts for loal and suite variables


    def post_variables(self):
        logger.info("++++++++++++++++++++++++++++++++++++++  INSIDE POST VARIABLES  ++++++++++++++++++++++++++++++++++++++")
        post_variables_str = self.pyprest_obj.post_variables
        if post_variables_str:

            # separate by ;
            variable_list = post_variables_str.split(";")
            for each in variable_list:
                each_item = each.split("=")

                # checking for syntax
                if "$[#" in each_item[0].strip(" "):
                    key = each_item[0].strip("set $[#").strip("Set $[#").strip("SET $[#").strip("]")

                    # find suite variables
                    if "SUITE." in str(each_item[0].strip(" ")):
                        key = "SUITE_" + each_item[0].strip(" ").strip("SUITE.").upper()
                        self.pyprest_obj.variables["suite"][key] = each_item[1].strip(" ")
                    else:
                        self.pyprest_obj.variables["local"][key] = each_item[1].strip(" ")
                    
                    # check for postdefined functions and response variables
                    if "$[#" in each_item[1].strip(" "):
                        # check for predefined function
                        
                        # if not found in predefined functions, check in response
                        response_key = each_item[1].strip("$[#").strip("]")
                        # find key in response  
                        # call keycheck
                        response_key_partition = response_key.split(".")
                        response_json = utils.format_resp_body(self.pyprest_obj.res_obj.response_body)
                        result = key_check(self.pyprest_obj).find_keys(response_json, deepcopy(response_key_partition), deepcopy(response_key_partition))

                        # if result is not "FOUND" then can't set value
                        if result.upper() is not "FOUND":
                            logger.info("====== Key Not Found in response =======")
                            logger.info("'" + key + "' is not found")
                            self.pyprest_obj.variables['local'][key] = each_item[1]
                        else:
                            new_list = utils.fetch_value_of_key(response_json, response_key_partition, result)
                            self.pyprest_obj.variables['local'][key] = new_list[response_key]

                    # key not found in response, checking pre variables
                    if "$[#" in each_item[1].strip(" "):
                        var_replacement(self.pyprest_obj).variable_replacement()
            print("variables dict after setting post variables: -------- ", self.pyprest_obj.variables)