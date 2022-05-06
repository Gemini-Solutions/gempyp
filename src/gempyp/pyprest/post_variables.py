import re
from pygem.pi_rest.key_check import key_check
from pygem.pi_rest import utils


class post_variables:
    def __init__(self, pirest_obj):
        self.pirest_obj = pirest_obj
        # get variable written in data["POST_VARIABLE"]
        # postdefined func
        # remove $[#]
        # assign_values and append to a dict
        # different dicts for loal and suite variables


    def post_variables(self):
        post_variables_str = self.pirest_obj.post_variables

        # separate by ;
        variable_list = post_variables_str.split(";")
        for each in variable_list:
            each_item = each.split("=")

            # setting normal varible
            if "$[#" in each_item[0].strip():
                key = each_item[0].strip("set $[#").strip("Set $[#").strip("SET $[#").strip("]")

                # find suite variables
                if "SUITE." in str(each_item[0].strip()):
                    key = "SUITE_" + each_item[0].strip().strip("SUITE.").upper()
                    self.pirest_obj.variables["suite"][key] = each_item[1].strip()
                else:
                    self.pirest_obj.variables["local"][key] = each_item[1].strip()
                

                # check for postdefined functions and response variables
                if "$[#" in each_item[1].strip():
                    # predefined function

                    response_key = each_item[1].strip("$[#").strip("]")
                    # find key in response  
                    # call keycheck
                    response_key_partition = response_key.split(".")

                    response_json = utils.format_resp_body(self.pirest_obj.res_obj.response_body)
                    result = key_check(self.pirest_obj).find_keys(response_json, response_key_partition, store_val=True)
                    # it will return the result along with the value of the key



        print("Setting post variables: -------- ", self.pirest_obj.variables)