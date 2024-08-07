import re
import logging as logger
from inspect import getmembers, isfunction
from gempyp.pyprest.predefinedFunctions import PredefinedFunctions as prefunc
import os
from gempyp.config import DefaultSettings
import copy


class VariableReplacement:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        if pyprest_obj.__dict__.get("variables") is not None:
            if self.pyprest_obj.variables.get("local") is not None:
                self.local_pre_variables = self.pyprest_obj.variables.get("local")
            if self.pyprest_obj.variables.get("suite") is not None:
                self.suite_pre_variables = self.pyprest_obj.variables.get("suite")
                
        self.global_variables = self.pyprest_obj.data.get("config_data")
        functions_list = [x[0] for x in getmembers(prefunc, isfunction)]
        self.functions_dict = {each.lower():each for each in functions_list}
        self.pyprest_obj.logger.info("**************  INSIDE VARIABLE REPLACEMENT  **************")


    def replaceToNull(self,data):
        logList = []
        for k,v in data.copy().items():
            if isinstance(v,dict):
                data[k] = self.replaceToNull(v)
            elif isinstance(v, list):
                for each in v:
                    if isinstance(each,dict):
                        self.replaceToNull(each)
            elif isinstance(v,str):
                if k!="PRE_VARIABLES" and k!="pre_variables" and k!="POST_VARIABLES" and k!="post_variables"  and k != "report_misc" and k !="REPORT_MISC" and  k is not None:
                    var_list = self.checkAndGetVariables(data[k])
                    for var in var_list:
                        var_name = var
                        var_val = self.getVariableValues(var_name)
                        if var_val == "null" and "$[#" in str(data[k]):
                            newValStr = data[k].replace(var_name, "Null")
                            logger.warning("-------Value of {0} not found!!! Assigning Null".format(var_name))
                        else:
                            newValStr = data[k].replace(var_name, str(var_val))
                        del data[k]
                        data[k] = newValStr         
        return data     
        

        
    def valueNotFound(self):
        logger.info("------ assigning all variables to null those value not found -----") 
        try:
            self.replaceToNull(self.pyprest_obj.__dict__)
            self.replaceToNull(self.pyprest_obj.reporter.template_data.__dict__)
        except Exception as e:
            print(e)


    def checkAndGetVariables(self, value_str) -> list:
        if value_str is not None and type(value_str) is str:
            self.value = value_str
            pattern = r"\$\[\S[a-zA-Z0-9_.]+\]"
            regex = re.compile(pattern) 
            variables = re.findall(regex,self.value)
            return variables
       
       
    def getVariableValues(self, var_name):
        varName = var_name.strip("$[#]").replace(" ","")
        try:
            if "GLOBAL.".casefold() in varName.casefold() and "$[#" not in self.pyprest_obj.__dict__["data"]["GLOBAL_VARIABLES"][varName.replace(".", "_").upper()]:
                 varValue = self.pyprest_obj.__dict__["data"]["GLOBAL_VARIABLES"][varName.replace(".", "_").upper()]
            # if "SUITE.".casefold() or "ENV.".casefold() in varName.casefold()
            if "SUITE.".casefold() in varName.casefold():  # ############ post 1.0.4
                varValue = self.suite_pre_variables[varName.replace(".", "_").upper()]
                print(varValue)
            else:
                varValue = self.local_pre_variables[varName]
                # suite_variables
                # varValue = self.local_pre_variables[varName]
            if "ENV.".casefold() in varName.casefold() and os.environ.get(varName.replace("ENV.","")):
                varValue = os.environ.get(varName.replace("ENV.",""))
        except:
            return "null"
        str_val = var_name.replace("$[#"+varName+"]", str(varValue))
        if "$[#" not in str_val:
            return str(str_val) 
        if "$[#" or "$" in str_val:
            return self.getVariableValues(str_val) 
    
    def getFunctionValues(self, var_name):
        func = var_name.strip("$[#]")
        func_items = func.split("(")
        func_name = func_items[0]
        params = func_items[1].strip(")")
        func_name = self.functions_dict.get(func_name.lower(), "invalid")

        try:
            val =  (prefunc + func_name)(params) if func_name != "invalid" else "null"
            return val
        except:
            return "null"
         

    def updateDataDictionary(self, data):
        for k,v in data.copy().items():
            if k == "GLOBAL_VARIABLES" and k == "GLOBAL_VARS":
                logger.info("global var")
                continue
            if isinstance(v,dict):
                data[k] = self.updateDataDictionary(v)
            elif isinstance(v,str):
                if k!="PRE_VARIABLES" and k!="pre_variables" and k!="POST_VARIABLES" and k!="post_variables"  and k != "report_misc" and k !="REPORT_MISC" and k is not None:
                    var_list = self.checkAndGetVariables(data[k])
                    for var in var_list:
                        var_name = var
                        var_val = self.getVariableValues(var_name)
                        if var_val == "null" and "$[#" in str(data[k]):
                            newValStr = data[k]
                        else:
                            newValStr = data[k].replace(var_name, str(var_val))
                        del data[k]
                        data[k] = newValStr
            
        return data

    
    def variableReplacement(self):
        if DefaultSettings.backup_data is None:
            DefaultSettings.backup_data =copy.deepcopy(self.pyprest_obj.__dict__["data"])
        self.updateDataDictionary(self.pyprest_obj.__dict__)
           
