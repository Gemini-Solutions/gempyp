import logging as logger
import re
from inspect import getmembers, isfunction
import traceback
from gempyp.pyprest.predefinedFunctions import PredefinedFunctions as Prefunc
from gempyp.pyprest.variableReplacement import VariableReplacement as VarReplace



class PreVariables:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        functions_list = [x[0] for x in getmembers(Prefunc, isfunction)]
        self.functions_dict = {each.lower(): each for each in functions_list}
        pattern_func = r"\$\[\S[a-zA-Z0-9_.]+\(.*\)\]"
        self.regex_func = re.compile(pattern_func)
        # get variable written in data["PRE_VARIABLE"]
        # predefined func
        # remove $[#]
        # assign_values and append to a dict
        # different dicts for loal and suite variables
        


    def preVariable(self):
        """
        Maintaining 2 types of dictionaries- local and suile level"""
        if(len(self.pyprest_obj.list_subtestcases)==0):
            self.pyprest_obj.variables["local"] = {}
            # self.pyprest_obj.variables["suite"] = {}
            self.pyprest_obj.variables["suite"] = self.pyprest_obj.data.get("SUITE_VARS",{})
        # print("self. suite vars in pre vars: ",self.pyprest_obj.data. )
        if self.pyprest_obj.pre_variables:
            self.pyprest_obj.logger.info("************** INSIDE PRE VARIABLES  **************")
            
            pre_variables_str = self.pyprest_obj.pre_variables

            # separate by ;
            variable_list = pre_variables_str.split(";")
            for each in variable_list:
                scope = 'local'
                each_item = each.split("=")
                if "SET" in each_item[0].upper() and '$[#' in each_item[0]:
                    # key = each_item[0].strip("set $[#").strip("Set $[#").strip("SET $[#").strip("]")
                    key = each_item[0].split("#")[1].replace("]","")
                    # find suite variables
                    if "SUITE." in key.upper():
                        scope = "suite"
                        key = key.replace(".", "_")
                    if "SUITE." in str(each_item[0].strip(" ")):
                        key = "SUITE_" + each_item[0].strip(" ").replace("set $[#SUITE.","").replace("]","").upper()
                        
                        self.pyprest_obj.variables["suite"][key] = self.getFunctionValues(each_item[1])

                    self.pyprest_obj.variables[scope][key] = self.getFunctionValues(each_item[1])
                    key = "SUITE_" + each_item[0].strip(" ").strip("set $[#SUITE.").strip("]").upper()
                    self.pyprest_obj.variables["suite"][key] = self.getFunctionValues(each_item[1].strip().replace(" ",""))
                    self.pyprest_obj.variables[scope][key] = self.getFunctionValues(each_item[1].strip().replace(" ",""))

                    
            self.pyprest_obj.logger.info(f"Setting PRE VARIABLES: -------- {str(self.pyprest_obj.variables)}")

    def getFunctionValues(self, var_name):
        if re.match(self.regex_func, var_name):
            functions_list = [x[0] for x in getmembers(Prefunc, isfunction)]
            self.functions_dict = {each.lower():each for each in functions_list}
            func = var_name.strip("$[#]")
            func_items = func.split("(")
            func_name = func_items[0]
            params = func_items[1].strip(")")
            data = VarReplace(self.pyprest_obj).updateDataDictionary({"params": params})
            func_name = self.functions_dict.get(func_name.lower(), "invalid")

            try:
                Prefunc_ = Prefunc(self.pyprest_obj)
                params = Prefunc_.parseParams(data["params"])
                func_name = getattr(Prefunc_, func_name) if func_name != "invalid" else None
                if func_name is not None:
                    val =  func_name(*params)
                else:
                    val = "Null"
                return val
            except:
                self.pyprest_obj.logger.info(traceback.format_exc())
                return "Null"
        else:
            return var_name.strip(" ")