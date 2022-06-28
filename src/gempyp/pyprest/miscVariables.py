from gempyp.pyprest.variableReplacement import VariableReplacement
import logging as logger


class MiscVariables:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        logger.info("+++++++++++++++++++++++++++  HNADLING MISC VARIABLES  +++++++++++++++++++++++++++")

  
    def miscVariables(self):
        try:
            if self.pyprest_obj.reporter.__dict__['_miscData'] is None:
                self.pyprest_obj.reporter.__dict__['_miscData'] = {}
        except Exception as e:
            print(e)
            logger.error(e)
        try:
            if self.pyprest_obj.report_misc:
                miscVariableStr = self.pyprest_obj.report_misc
                print(miscVariableStr)
                miscVariableList = miscVariableStr.split(";")
                for each in miscVariableList:
                    each_item = each.split("=")
                    if "$[#" in each_item[0].strip(" "):
                        key = each_item[0].strip("set $[#").strip("Set $[#").strip("SET $[#").strip("]")
                        if "$[#" in each_item[1]:
                            self.value = VariableReplacement(self.pyprest_obj).getVariableValues(each_item[1].strip(" "))
                            self.pyprest_obj.reporter._miscData[key.replace("misc.","").upper()] = self.value.upper()
                            logger.info(f"----- ADDED MISC VARIABLE WITH KEY: {key} & VALUE: {self.value} ------")
                        else:
                            self.pyprest_obj.reporter._miscData[key.replace("misc.","").upper()] = each_item[1].strip(" ").upper()
                            logger.info(f"----- ADDED MISC VARIABLE WITH KEY: {key.strip('misc.').upper()} & VALUE: {each_item[1].strip(' ')} ------")

        except Exception as e:
            logger.error(e)
        self.pyprest_obj.reporter.addMisc("k1","v1")
        logger.info(f"Report_misc_variables:  { self.pyprest_obj.reporter._miscData } ")

        
