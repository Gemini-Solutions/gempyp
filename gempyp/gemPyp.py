from gempyp.config.xmlConfig import XmlConfig
import argparse
from gempyp.engine.engine import Engine
from gempyp.libs.common import download_common_file
from gempyp.data_uploader import dataUploader
import logging

class Gempyp:
    def __init__(self):
        """
        initiating some variables  
        """
        self.config = None
        self.MAIL = None
        self.PROJECT_NAME = None
        self.REPORT_NAME = None
        self.MODE = None
        self.ENVIRONMENT = None
        self.args = {}
        self.THREADS = None
        self.JEWEL_BRIDGE_TOKEN = None 
        self.REPORT_LOCATION = None
        self.CATEGORY=None
        self.JEWEL_USER=None
        self.S_RUN_ID = None
        self.TESTCASE_LIST = None
        self.ENTER_POINT = None
        self.S_ID = None
        self.RUN_TYPE = None
        self.RUN_MODE = None
        self.RE_RUN = None
    
    def argParser(self):
        """Argument parser to help running through CLI"""

        parser = argparse.ArgumentParser()
        parser.add_argument('-config','-c',dest='config',type=str, required=False, help='Path of config file. Accepts both absolute and relative path.')
        parser.add_argument('-mailTo','-mailTo',dest='MAIL-TO', type=str, required=False, help='Specify recipient email addresses.Can send multiple email id by comma separated.')
        parser.add_argument('-mailCc','-mailCc',dest='MAIL-CC', type=str, required=False, help='Provide email addresses for carbon copy (cc).Can send multiple email id by comma separated.')
        parser.add_argument('-mailBcc','-mailBcc',dest='MAIL-BCC', type=str, required=False, help='Specify BCC email addresses.Can send multiple email id by comma separated.')
        parser.add_argument('-project','-p',dest='PROJECT_NAME', type=str, required=False, help='Specify project name.')
        parser.add_argument('-Report_name','-rn',dest='REPORT_NAME', type=str, required=False, help='Specify report name.')
        parser.add_argument('-mode','-mode',dest='MODE', type=str, required=False, help='Specify execution mode. Values can be sequence and optimize.')
        parser.add_argument('-env','-env',dest='ENVIRONMENT', type=str, required=False,help='Specify the testing environment.' )
        parser.add_argument('-threads','-t',dest='THREADS',type=int, required=False, help='Number of threads use in optimoize mode. This should be a numeric value.')
        parser.add_argument('-bridge_token','-token',dest='JEWEL_BRIDGE_TOKEN',type=str, required=False, help='Jewel bridge token.')
        parser.add_argument('-username','-username',dest='JEWEL_USER',type=str, required=False, help='Jewel username.')
        parser.add_argument('-report_location','-rl',dest='REPORT_LOCATION',type=str, required=False, help='Location for jewel report. Can ba absolute and relative path.')
        parser.add_argument('-category','-category',dest='CATEGORY',type=str, required=False, help='Category of testcases you want to run.')
        parser.add_argument('-run_id','-run_id',dest='S_RUN_ID',type=str, required=False, help='For specifying s_run_id.')
        parser.add_argument('-tc','-testcase_list',dest='TESTCASE_LIST',type=str, required=False, help='Name of testcases user want to run. User can pass multiple testcases in coma separated form.')
        parser.add_argument('-enter_point','-enter_point',dest='ENTER_POINT',type=str, required=False, help='Base Url user want to use for API. This should be a url.')
        parser.add_argument('-s_id','-s_id',dest='S_ID',type=str, required=False)
        parser.add_argument('-run_type','-run_type',dest='RUN_TYPE',type=str, required=False)
        parser.add_argument('-run_mode','-run_mode',dest='RUN_MODE',type=str, required=False)
        parser.add_argument('-rerun','-rerun',dest='RE_RUN',type=str, required=False, help='Specify the path of json file you want to create report for. This should json file and created by gempyp in case of Apis failure.')

        args = parser.parse_args()
        return args

    def runner(self):
        """
        This function takes the config and updates the config data in case or cli run and direct(python) run
        """
        s_run_id = vars(self)["S_RUN_ID"]
        if self.args.get('RE_RUN',None) != None:
                print("Trying to Reupload Data")
                dataUploader(self.args.get('RE_RUN'),self.args.get('JEWEL_BRIDGE_TOKEN',None))
        elif self.RE_RUN != None:
                print("Trying to Reupload Data")
                dataUploader(self.RE_RUN, self.JEWEL_BRIDGE_TOKEN)
        # if self.args.RE_RUN
        else:
            file_path=download_common_file(self.config)
            config=XmlConfig(file_path,s_run_id)
            if not self.args:
                del self.__dict__["args"]
                config.cli_config = vars(self)
            else:
                config.cli_config = self.args
            config.update()
            Engine(config)

    def parser(self):
        """Calls the parser and handles the case of no cli args"""
        args = self.argParser()
        if args.config != None:
            self.config = args.config
        self.args = vars(args)
        self.runner()

def main():
    obj = Gempyp()
    #obj.config = "C:\\Users\\an.pandey\\gempyp\\tests\\configTest\\Gempyp_Test_Suite.xml"
    #obj.ENV = ""
    #obj.MAIL = ""
    obj.parser()

if __name__ == "__main__":
    obj = Gempyp()
    
    #obj.config = "C:\\Users\\an.pandey\\gempyp\\tests\\configTest\\Gempyp_Test_Suite.xml"
    #obj.ENV = ""
    #obj.MAIL = ""
    obj.parser()
    

