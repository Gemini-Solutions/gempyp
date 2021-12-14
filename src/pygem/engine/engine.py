import sys
import os
import logging
import platform
import getpass
import uuid
from datetime import datetime
from testData import testData
from status import status

class Engine():
    def __init__(self,params_config):
        self.Executor(self, params_config)
        pass

    def run(self,params_config):
        logging.info("Engine Started")
        self.DATA = testData()
        # get the env for the engine Runner
        self.ENV = os.getenv("ENV_BASE","BETA").upper()
        # initial SETUP
        self.setUP(params_config)
        self.parseMails()
        self.parseConfig()
        self.makeSuiteDetails()
        self.makeRunDetails()
        self.start()
        self.cleaup()



    
    def setUP(self, config):
        self.PARAMS = config
        self.machine = platform.node()
        self.user = getpass.getuser()
        self.current_dir = os.getcwd()
        self.platform = platform.system()
        self.start_time = datetime.utcnow()

    def parseMails(self):
        if os.path.isfile(self.PARAMS.mail):
            with open(self.PARAMS.mail,'r') as mail_file:
                self.mail = mail_file.read()
            return
        
        self.mail = self.PARAMS.mail

    #TODO
    def parseConfig(self):
        pass

    def makeSuiteDetails(self):
        
        self.s_run_id = f"{self.projectName}_{self.project_env}_{uuid.uuid4()}"
        self.s_run_id = self.s_run_id.upper()
        SuiteDetails ={
            "s_run_id":self.s_run_id,
            "s_start_time":self.start_time,
            "s_end_time":None,
            "status": status.EXE.name,
            "project_name": self.projectName,
            "run_type": "ON DEMAND",
            "s_report_type": self.reportName
        }

        self.DATA.suiteDetail = self.DATA.suiteDetail.append(SuiteDetails, ignore_index = True)
    

    def makeRunDetails(self):
        self.r_run_id = f"MR_{self.projectName}_{self.project_env}_{uuid.uuid4()}"
        self.r_run_id = self.r_run_id.upper()
        RunDetails ={
            "r_run_id":self.r_run_id,
            "s_run_id":self.s_run_id,
            "r_start_time":self.start_time,
            "r_end_time":None,
            "user":self.user,
            "status":status.EXE.name,
            "env":self.project_env,
            "machine":self.machine,
            "run_type":"ON DEMAND",
            "initiated_by":self.user,
            "run_mod":"LINUX_CLI" 

        }

        self.DATA.multiRunColumns = self.DATA.multiRunColumns.append(RunDetails,ignore_index=True)


    def start(self):
        pass
        
        
    def cleaup(self):
        pass
