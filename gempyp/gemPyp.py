from gempyp.config.xmlConfig import XmlConfig
import argparse
from gempyp.engine.engine import Engine

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
        self.CATEGORY = None
        self.SET = None
    
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
        parser.add_argument('-set','-set',dest='SET',type=str, required=False)

        args = parser.parse_args()
        return args

    def runner(self):
        """
        This function takes the config and updates the config data in case or cli run and direct(python) run
        """
        config = XmlConfig(self.config)
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
    

