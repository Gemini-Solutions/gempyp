from gempyp.config.xmlConfig import XmlConfig
from gempyp.pyprest.pyprest import PYPREST
from gempyp.config.baseConfig import abstarctBaseConfig
from typing import Type
import getpass
import platform
import argparse
import os
import datetime
from datetime import timezone, datetime


class R_ENGINE:
    def __init__(self, **kwargs):
        # parse cli to get restcase name
        parser = argparse.ArgumentParser()
        self.args = self.parse_arguments(parser)
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
        self.setUP(config)
        data = self.form_data(config, self.tcname)
        PYPREST(data).rest_engine()
        print("-----end-------")

    def form_data(self, config: Type[abstarctBaseConfig], tcname):
        data = {}
        # get the testcase list from config and check for the passed testcase
        
        if tcname.upper() in self.CONFIG.getTestcaseConfig().keys():
            self.PARAMS = config.getSuiteConfig()
            data["configData"] = config.getTestcaseData(tcname)
            data["PROJECTNAME"] = self.PARAMS["PROJECT"]
            data["ENV"] = self.PARAMS["ENV"]
            # data["S_RUN_ID"] = ""
            data["USER"] = getpass.getuser()
            data["MACHINE"] = platform.node()
            data["OUTPUT_FOLDER"] = ""
        return data

    def setUP(self, config: Type[abstarctBaseConfig]):
        self.PARAMS = config.getSuiteConfig()
        self.CONFIG = config
        self.machine = platform.node()
        self.user = getpass.getuser()
        self.current_dir = os.getcwd()
        self.platform = platform.system()
        self.start_time = datetime.now(timezone.utc)
        self.projectName = self.PARAMS["PROJECT"]
        self.reportName = self.PARAMS.get("REPORTNAME")
        self.project_env = self.PARAMS["ENV"]

    def parse_arguments(self, parser):
        parser.add_argument("-t", "--testcase",dest="testcase", help="name of the testcase to run")
        parser.add_argument("-config", "--config", help="config file")
        args = parser.parse_args()
        return args


if __name__ == "__main__":
    config = XmlConfig('C:\\Users\\an.pandey\\gempyp\\tests\\configTest\\sampleTest.xml')
    tcname = "REST_COUNTRIES_3"
    R_ENGINE(data=config, tcname=tcname)