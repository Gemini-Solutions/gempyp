import json
import re

class variable_replacement:
    def __init__(self, pirest_obj):
        self.pirest_obj = pirest_obj
        print(pirest_obj.__dict__)
        if pirest_obj.__dict__.get("variables") is not None:
            self.pre_variables = pirest_obj.__dict__.get("variables")
        if self.pre_variables.get("local") is not None:
            self.local_pre_variables = self.pre_variables.get("local")
        if self.pre_variables.get("suite") is not None:
            self.suite_pre_variables  = self.pre_variables.get("suite")

        print("+++++++++++++++++")
        print(self.pre_variables)
        print(self.local_pre_variables)
        print(self.suite_pre_variables)
        print("+++++++++++++++++")

        # self.pre_variables.suite_variable = self.pirest_obj.__dict__.get("variables").get("suite")


        print("+++++++++++++++++++++++++++++++++++++++++")

        print("INSIDE VARIABLE REPLACEMENT")
        # print("Before variable update:  ",self.pirest_obj.__dict__.get("data")["configData"])
        # for key,value in pirest_obj.__dict__.get("data")["configData"].items():
        #     if self.checkVariables(key,str(value)):
        #         print(f"variable present in {key}")
        #         # print(key,"   ",value)
        # self.variable_replacement()

        
        # print("After variable update:  ",self.pirest_obj.__dict__.get("data")["configData"])
        print("+++++++++++++++++++++++++++++++++++++++++")

    # def checkVariables(self,key, value):
    #     self.value = value
    #     pattern = r"\$\[\S[a-zA-Z0-9_.]+\]"
    #     regex = re.compile(pattern)
    #     variables = re.findall(regex,self.value)
    #     if variables is not None and len(variables)!=0:
    #         # print(variables)
    #         for each in variables:
    #             if key != "PRE_VARIABLES":
    #                 # print(f"before update value: {value}")
    #                 each_key_to_replace = str(each)
    #                 # print("key to replace are: ", each_key_to_replace)
    #                 self.update_dict = {}
    #                 while(self.update_dict is None or self.update_dict[key].contains("$[")):
    #                     self.update_dict[key] = self.value.replace("$[#"+each_key_to_replace.strip("$[#]")+"]",self.value_for_local_pre_variables(each_key_to_replace.strip("$[#]")))
    #                     print(f" after update value for {each_key_to_replace}  {self.update_dict}  ")
    #                 if "$" in self.update_dict[key]:
    #                     self.checkVariables(self.update_dict[key])
    #                 else:
    #                      self.pirest_obj.__dict__.get("data")["configData"].update(self.update_dict)
    #         return True
    #     else:
    #         return False
    # def value_for_local_pre_variables(self, variable_name):
    #     if self.local_pre_variables is not None and variable_name in self.local_pre_variables:
    #         print("inside values : asking for value of ",variable_name )
    #         print("value is ", self.local_pre_variables[variable_name])
    #         return self.local_pre_variables[variable_name]
    #     else: 
    #         return "Null"

    def check_and_get_variables(self,value_str) -> list:
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
        
        




    def variable_replacement(self):
        """
        invocation workflow
        iterate one by one through all the key:val pairs in pirest_obj.__dict__.["data"]["configdata"].items()
            -- 


        functions used check_and_get_variables for every values using regex and return the list of the variables [].
        iterate through each values get their actual value and then replace in the string and update the config dictionary.
        
        
        """


        configDictionary = self.pirest_obj.__dict__["data"]["configData"]
        for key,value in configDictionary.items():
            self.vars = self.check_and_get_variables(value)
            if self.vars is not None and len(self.vars)>0 and key !=  "PRE_VARIABLES" :
                print(f"Variables are present in {key} : {value} and variable list is {self.vars}")
                for i in range(len(self.vars)):
                    var_name = self.vars[i]
                    print(f"var_name: {var_name}")
                    var_value = self.getVariableValues(var_name)
                    print(f"var_value: {var_value}")
                    update_dict  = {}
                    update_dict[key] = value.replace(var_name, var_value)
                    # print(value.replace(var_name, var_value))
                    print(f"update dict = {update_dict}")
                    # self.configDictionary[key]
                    configDictionary.update(update_dict)
                    # print(self.configDictionary[key])
            
        print("updated: ",configDictionary)
        self.pirest_obj.__dict__["data"]['method'] = 'GET'
        print("previous dictionary:  ",self.pirest_obj.__dict__["data"]['method'])
        


