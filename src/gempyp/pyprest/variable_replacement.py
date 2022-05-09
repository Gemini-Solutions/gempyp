import re
import json

class variable_replacement:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        if pyprest_obj.__dict__.get("variables") is not None:
            if self.pyprest_obj.variables.get("local") is not None:
                self.local_pre_variables = self.pyprest_obj.variables.get("local")
            if self.pyprest_obj.variables.get("suite") is not None:
                self.suite_pre_variables  = self.pyprest_obj.variables.get("suite")
            
        print("+++++++++++++++++++++++++++++++++++++++++")
        print("INSIDE VARIABLE REPLACEMENT")
        print("+++++++++++++++++++++++++++++++++++++++++")


    def check_and_get_variables(self, value_str) -> list:
        if value_str is not None and type(value_str) is str:
            self.value = value_str
            pattern = r"\$\[\S[a-zA-Z0-9_.]+\]"
            regex = re.compile(pattern) 
            variables = re.findall(regex,self.value)
            return variables
       
       
    def getVariableValues(self, var_name):
        # print("start getVariableValues ")
        varName = var_name.strip("$[#]")
        # print(f"varName:  {varName}")
        varValue = self.local_pre_variables[varName]
        # print(f"varValue:  {varValue}")
        str_val = var_name.replace("$[#"+varName+"]",varValue)

        if "$[#" not in str_val:
            # print(str_val,"  inside if")
            # print("end getVariableValues ")
            return str(str_val)  
        if "$[#" in str_val:
            # print("still variable calling again")
            return self.getVariableValues(str_val) 


    def update_data_dictionary(self, data):
        for k,v in data.copy().items():
            if isinstance(v,dict):
                data[k] = self.update_data_dictionary(v)
            elif isinstance(v,str):
                if k!="PRE_VARIABLES" and k!="pre_variables" and k is not None:
                    # print(k,data[k])
                    var_list = self.check_and_get_variables(data[k])
                    for var in var_list:
                        var_name = var
                        var_val = self.getVariableValues(var_name)
                        # print("+++VarVal+++\n",var_val,"\n+++++++++++")
                        newValStr = data[k].replace(var_name, var_val)
                        # print("++++newvalstr++++\n",newValStr,"\n+++++++++++++++++")
                        del data[k]
                        data[k] = newValStr
        return data

    def variable_replacement(self):
        print(self.local_pre_variables)

        self.update_data_dictionary(self.pyprest_obj.__dict__)
        print(self.local_pre_variables)
        

        # newDict = self.pyprest_obj.__dict__
        # reporterVal = newDict['reporter']
        # print(type(reporterVal))
        # del(newDict['reporter'])
        # newDict['reporter'] = str(reporterVal)

        # newJson = json.dumps(newDict, indent = 4)
        # print(newJson)

        # print(self.pyprest_obj.__dict__)

