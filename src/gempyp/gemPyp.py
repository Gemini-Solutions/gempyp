from gempyp.config.xmlConfig import XmlConfig
from gempyp.engine.engine import Engine
import argparse


class GemPyp:
    def __init__(self):
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


    
    def argParser(self):
        """Agument parser to help running through CLI"""

        parser = argparse.ArgumentParser()
        parser.add_argument('-config','-c',dest='config',type=str, required=False)
        parser.add_argument('-mail','-m',dest='MAIL', type=str, required=False)
        parser.add_argument('-project','-p',dest='PROJECT', type=str, required=False)

        parser.add_argument('-Report_name','-rn',dest='REPORT_NAME', type=str, required=False)
        parser.add_argument('-mode','-mode',dest='MODE', type=str, required=False)
        parser.add_argument('-env','-env',dest='ENV', type=str, required=False)
        parser.add_argument('-threads','-t',dest='THREADS',type=str, required=False)
        parser.add_argument('-bridge_token','-token',dest='BRIDGE_TOKEN',type=str, required=False)
        parser.add_argument('-output_folder','-of',dest='OUTPUT_FOLDER',type=str, required=False)

        args = parser.parse_args()
        return args

    def runner(self):
        """This function takes the config and updates the config data in case or cli run and direct(python) run"""
        config = XmlConfig(self.config)
        print(config.__dict__)
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

if __name__ == "__main__":
    obj = GemPyp()
    
    obj.config = "C:\\Users\\an.pandey\\gempyp\\tests\\configTest\\Gempyp_Test_Suite.xml"
    obj.ENV = "beta"
    obj.MAIL = ""
    obj.parser()
    

