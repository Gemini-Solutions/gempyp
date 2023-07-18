from gempyp.pyprest.variableReplacement import VariableReplacement
import logging


class MiscVariables:
    def __init__(self, pyprest_obj):
        self.pyprest_obj = pyprest_obj
        logging.info("+++++++++++++++++++++++++++  HANDLING MISC VARIABLES  +++++++++++++++++++++++++++")

  
    def miscVariables(self):
        try:
            if self.pyprest_obj.reporter.__dict__['_misc_data'] is None:
                self.pyprest_obj.reporter.__dict__['_misc_data'] = {}
        except Exception as e:
            logging.info(e)
            logging.error(e)
        try:
            if self.pyprest_obj.report_misc:
                misc_variable_str = self.pyprest_obj.report_misc
                misc_variable_list = misc_variable_str.split(";")
                for each in misc_variable_list:
                    each_item = each.split("=")
                    if "$[#" in each_item[0].strip(" "):
                        key = each_item[0].strip("set $[#").strip("Set $[#").strip("SET $[#").strip("]")
                        if "$[#" in each_item[1]:
                            self.value = VariableReplacement(self.pyprest_obj).getVariableValues(each_item[1].strip(" "))
                            self.pyprest_obj.reporter._misc_data[key.replace("misc.","").upper()] = self.value.upper()
                            logging.info(f"----- ADDED MISC VARIABLE WITH KEY: {key} & VALUE: {self.value} ------")
                        else:
                            self.pyprest_obj.reporter._misc_data[key.replace("misc.","").upper()] = each_item[1].strip(" ").upper()
                            logging.info(f"----- ADDED MISC VARIABLE WITH KEY: {key.strip('misc.').upper()} & VALUE: {each_item[1].strip(' ')} ------")

        except Exception as e:
            logging.error(e)
        # logging.info(f"Report_misc_variables:  { self.pyprest_obj.reporter._misc_data }")

        
