import re
import logging as logger

class VariableReplacement:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        if pyprest_obj.__dict__.get("variables") is not None:
            if self.pyprest_obj.variables.get("local") is not None:
                self.local_pre_variables = self.pyprest_obj.variables.get("local")
            if self.pyprest_obj.variables.get("suite") is not None:
                self.suite_pre_variables = self.pyprest_obj.variables.get("suite")
            
        logger.info("++++++++++++++++++++++++++++++++++++++  INSIDE VARIABLE REPLACEMENT  ++++++++++++++++++++++++++++++++++++++")



    def checkAndGetVariables(self, value_str) -> list:
        if value_str is not None and type(value_str) is str:
            self.value = value_str
            pattern = r"\$\[\S[a-zA-Z0-9_.]+\]"
            regex = re.compile(pattern) 
            variables = re.findall(regex,self.value)
            return variables
       
       
    def getVariableValues(self, var_name):
        varName = var_name.strip("$[#]")
        # predefined_funtions().replace_funtion_with_value()
        # varValue = self.local_pre_variables.get(varName, "$NULL")  #  $NULL means a variable does not exist but is still being used. This might be a case of post varibles or predefined functions.
        # varValue = self.local_pre_variables.get(varName, "$[#"+varName+"]")
        try:
            """if "SUITE." in varName.upper():
                varValue = self.suite_pre_variables["SUITE_" + varName.rstrip("suite.").rstrip("SUITE.")]
            else:
                varValue = self.local_pre_variables[varName]
                # suite_variables"""
            varValue = self.local_pre_variables[varName]
        except:
            return "Null"
        str_val = var_name.replace("$[#"+varName+"]",varValue)
        if "$[#" not in str_val:
            return str(str_val) 
        if "$[#" or "$" in str_val:
            return self.getVariableValues(str_val) 


    def updateDataDictionary(self, data):
        for k,v in data.copy().items():
            if isinstance(v,dict):
                data[k] = self.updateDataDictionary(v)
            elif isinstance(v,str):
                if k!="PRE_VARIABLES" and k!="pre_variables" and k!="POST_VARIABLES" and k!="post_variables"  and  k is not None:
                    var_list = self.checkAndGetVariables(data[k])
                    for var in var_list:
                        var_name = var
                        var_val = self.getVariableValues(var_name)
                        if var_val == "Null" and "$[#" in str(data[k]):
                            newValStr = data[k]
                        else:
                            newValStr = data[k].replace(var_name,var_val)
                        del data[k]
                        data[k] = newValStr
                    
        return data

    def variableReplacement(self):
        # print(self.local_pre_variables)
        data = self.updateDataDictionary(self.pyprest_obj.__dict__)
