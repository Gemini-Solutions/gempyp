from gempyp.config.xmlConfig import XmlConfig
import argparse
from gempyp.engine.engine import Engine
from gempyp.config.GitLinkXML import fetchFileFromGit

class Gempyp:
    def __init__(self):
        """
        initiating some variables  
        """
        self.config = None
        self.MAIL = None
        self.PROJECT = None
        self.REPORT_NAME = None
        self.MODE = None
        self.ENV = None
        self.args = None
        self.THREADS = None
        self.BRIDGE_TOKEN = None 
        self.OUTPUT_FOLDER = None
        self.CATEGORY=None
        self.USERNAME=None
        self.RUN_ID = None
        self.TESTCASE_LIST = None
        self.BASE_URL = None
        self.S_ID = None
        self.RUN_TYPE = None
        self.RUN_MODE = None
    
    def argParser(self):
        """Argument parser to help running through CLI"""

        parser = argparse.ArgumentParser()
        parser.add_argument('-config','-c',dest='config',type=str, required=False)
        parser.add_argument('-mail','-m',dest='MAIL', type=str, required=False)
        parser.add_argument('-project','-p',dest='PROJECT', type=str, required=False)
        parser.add_argument('-Report_name','-rn',dest='REPORT_NAME', type=str, required=False)
        parser.add_argument('-mode','-mode',dest='MODE', type=str, required=False)
        parser.add_argument('-env','-env',dest='ENV', type=str, required=False)
        parser.add_argument('-threads','-t',dest='THREADS',type=str, required=False)
        parser.add_argument('-bridge_token','-token',dest='BRIDGE_TOKEN',type=str, required=False)
        parser.add_argument('-username','-username',dest='USERNAME',type=str, required=False)
        parser.add_argument('-output_folder','-of',dest='OUTPUT_FOLDER',type=str, required=False)
        parser.add_argument('-category','-category',dest='CATEGORY',type=str, required=False)
        parser.add_argument('-run_id','-run_id',dest='RUN_ID',type=str, required=False)
        parser.add_argument('-tc','-testcase_list',dest='TESTCASE_LIST',type=str, required=False)
        parser.add_argument('-base_url','-base_url',dest='BASE_URL',type=str, required=False)
        parser.add_argument('-s_id','-s_id',dest='S_ID',type=str, required=False)
        parser.add_argument('-run_type','-run_type',dest='RUN_TYPE',type=str, required=False)
        parser.add_argument('-run_mode','-run_mode',dest='RUN_MODE',type=str, required=False)

        args = parser.parse_args()
        return args

    def runner(self):
        """
        This function takes the config and updates the config data in case or cli run and direct(python) run
        """
        s_run_id = vars(self)["RUN_ID"]
        if("GIT" in self.config):
            list_url=self.config.split(":")
            
            config=XmlConfig(fetchFileFromGit(list_url[2],list_url[3],list_url[4],list_url[5]),s_run_id)
        else:
            config = XmlConfig(self.config, s_run_id)
        if not self.args:
            del self.__dict__["args"]
            config.cli_config = vars(self)
        else:
            config.cli_config = vars(self.args)
        config.update()
        Engine(config)

    def parser(self):
        """Calls the parser and handles the case of no cli args"""
        args = self.argParser()
        if args.config != None:
            self.config = args.config
        self.args = args
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
    

