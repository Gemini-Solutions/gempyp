import re
from gempyp.pyprest.key_check import key_check
from gempyp.pyprest import utils


class post_variables:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        # get variable written in data["POST_VARIABLE"]
        # postdefined func
        # remove $[#]
        # assign_values and append to a dict
        # different dicts for loal and suite variables


    def post_variables(self):
        post_variables_str = self.pyprest_obj.post_variables
        if post_variables_str:

            # separate by ;
            variable_list = post_variables_str.split(";")
            for each in variable_list:
                each_item = each.split("=")

                # setting normal varible
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
                        # predefined function

                        response_key = each_item[1].strip("$[#").strip("]")
                        # find key in response  
                        # call keycheck
                        response_key_partition = response_key.split(".")

                        response_json = utils.format_resp_body(self.pyprest_obj.res_obj.response_body)
                        result = key_check(self.pyprest_obj).find_keys(response_json, response_key_partition, store_val=True)
                        # it will return the result along with the value of the key



            print("Setting post variables: -------- ", self.pyprest_obj.variables)