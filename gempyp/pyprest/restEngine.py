import logging
from gempyp.config.xmlConfig import XmlConfig
from gempyp.pyprest.pypRest import PypRest
from gempyp.config.baseConfig import AbstarctBaseConfig
from typing import Type
import getpass
import platform
import argparse
import os
import datetime
from datetime import timezone, datetime


class REngine:
    def __init__(self, **kwargs):
        # parse cli to get restcase name
        parser = argparse.ArgumentParser()
        self.args = self.parseArguments(parser)
        if (self.args.testcase and self.args.config):
            self.path = self.args.config
            self.tcname = self.args.testcase
            self.config = XmlConfig(self.path)
        else:
            self.tcname = kwargs.get("tcname", None)
            self.config = kwargs.get("data", None)
        self.runner()
        pass

    def runner(self):
        config = self.config
        self.setUp(config)
        data = self.formData(config, self.tcname)
        PypRest(data).restEngine()
        logging.info("-----end-------")

    def formData(self, config: Type[AbstarctBaseConfig], tcname):
        data = {}
        # get the testcase list from config and check for the passed testcase
        
        if tcname.upper() in self.CONFIG.getTestcaseConfig().keys():
            self.PARAMS = config.getSuiteConfig()
            data["config_data"] = config.getTestcaseData(tcname)
            data["PROJECT_NAME"] = self.PARAMS["PROJECT"]
            data["ENV"] = self.PARAMS["ENV"]
            # data["S_RUN_ID"] = ""
            data["USER"] = getpass.getuser()
            data["MACHINE"] = platform.node()
            data["OUTPUT_FOLDER"] = ""
        return data

    def setUp(self, config: Type[AbstarctBaseConfig]):
        self.PARAMS = config.getSuiteConfig()
        self.CONFIG = config 
        self.machine = platform.node()
        self.user = getpass.getuser()
        self.current_dir = os.getcwd()
        self.platform = platform.system()
        self.start_time = datetime.now(timezone.utc)
        self.project_name = self.PARAMS["PROJECT"]
        self.report_name = self.PARAMS.get("REPORTNAME")
        self.project_env = self.PARAMS["ENV"]

    def parseArguments(self, parser):
        parser.add_argument("-t", "--testcase",dest="testcase", help="name of the testcase to run")
        parser.add_argument("-config", "--config", help="config file")
        args = parser.parse_args()
        return args


if __name__ == "__main__":
    config = XmlConfig('C:\\Users\\an.pandey\\gempyp\\tests\\configTest\\sampleTest_pyprest.xml')
    tcname = "GOREST"
    REngine(data=config, tcname=tcname)