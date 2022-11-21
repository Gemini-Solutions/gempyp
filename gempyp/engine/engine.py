from pathlib import Path
import sys
import os
import platform
import getpass
import json
import traceback
from multiprocessing import Pool
from typing import Dict, List, Tuple, Type
from unittest import TestCase
import uuid
from datetime import datetime, timezone
from gempyp.config.baseConfig import AbstarctBaseConfig
from gempyp.engine.testData import TestData
from gempyp.libs.enums.status import status
from gempyp.reporter.reportGenerator import TemplateData
from gempyp.libs import common
from gempyp.engine.runner import testcaseRunner, getError
from gempyp.config import DefaultSettings
import logging
from gempyp.libs.logConfig import my_custom_logger, LoggingConfig
from gempyp.engine import dataUpload
from gempyp.pyprest.pypRest import PypRest
import smtplib
from gempyp.dv.dvRunner import DvRunner
from gempyp.jira.jiraIntegration import jiraIntegration, addComment
from multiprocessing import Process, Pipe



def executorFactory(data: Dict,conn= None, custom_logger=None) -> Tuple[List, Dict]:
    
    """
    calls the differnt executors method based on testcase type e.g. gempyp,pyprest,dvm
    Takes single testcase data as input
    """

    print("--------- In Executor Factory ----------\n")


    if not custom_logger:
        log_path = os.path.join(os.environ.get('TESTCASE_LOG_FOLDER'),data['config_data'].get('NAME') + '_'
        + os.environ.get('unique_id') + '.log')
        custom_logger = my_custom_logger(log_path)
        LoggingConfig(log_path)
    data['config_data']['LOGGER'] = custom_logger
    if 'log_path' not in data['config_data']:
        data['config_data']['LOG_PATH'] = log_path
    

    
    # engine_control = {"pyprest": {"function": PypRest(data).restEngine(), "log": custom_logger.info("Starting the PYPREST testcase")},
    # "dvm": {"function": DvmRunner(data).dvmEngine(), "log": custom_logger.info("Starting the DVM testcase")}, 
    # "gempyp": {"function": testcaseRunner(data), "log": custom_logger.info("Starting the GEMPYP testcase")}}
    engine_control = {
        "pyprest":{"class": PypRest, "classParam": data, "function": "restEngine"},
        "dv":{"class": DvRunner, "classParam": data, "function": "dvEngine"},
        "gempyp":{"function": testcaseRunner, "functionParam": data}
    }

    _type = data.get("config_data").get("TYPE","GEMPYP")
    dv = ["data validator","dv","datavalidator","dvalidator"]
    if _type in dv:
        _type = "dv"

    _type = data.get("config_data")["TYPE"]
    dv = ["data validator","dv","datavalidator","dvvalidator"]
    if _type in dv:
        _type = "dv"

    _type_dict = engine_control[_type.lower()]
    custom_logger.info(f"Starting {_type} testcase")

    if _type_dict.get("class", None):
        data =  getattr(_type_dict["class"](_type_dict['classParam']), _type_dict['function'])()  # need to make it generic for functionParam too
    else:
        data =  _type_dict["function"](_type_dict["functionParam"])  # we need to dissolve this else condition too somehow
    if conn == None:
        return data
    else:
        conn.send([data])
        conn.close()

    """if "TYPE" not in data["config_data"] or data["config_data"].get("TYPE").upper() == "GEMPYP":
        custom_logger.info("starting the GemPyP testcase")
        #custom_logger.setLevel(logging.INFO)
        return testcaseRunner(data)

    elif data["config_data"].get("TYPE").upper() == "DVM":
        # TODO do the DVM stuff
        logging.info("starting the DVM testcase")
        return DvmRunner(data).dvmEngine()

    elif data["config_data"].get("TYPE").upper() == "PYPREST":
        # TODO do the resttest stuff here
        custom_logger.info("starting the PYPREST testcase")
        try:
            return PypRest(data).restEngine()
        except Exception as e:
            traceback.print_exc()
            return None, getError(e, data["config_data"])"""


class Engine:
    def __init__(self, params_config):
        """
        constructor used to  call run method
        takes config as input
        """
        # logging.basicConfig()
        # logging.root.setLevel(logging.DEBUG)
        self.run(params_config)
        

    def run(self, params_config: Type[AbstarctBaseConfig]):
        """
        main method to call other methods that are required for report generation
        takes config as input
        """
        logging.info("Engine Started")
        # initialize the data class
        

        self.DATA = TestData()
        # get the env for the engine Runner
        self.ENV = os.getenv("ENV_BASE", "BETA").upper()
        # initial SETUP
        self.setUP(params_config)
        self.parseMails()
        self.makeSuiteDetails()
        #jewel variable is to print jewel link in rep summary
        self.jewel = ''
        unuploaded_path = ""
        failed_Utestcases = 0
        #trying first rerun of base url api in case of api failure
        if self.PARAMS.get("BASE_URL", None) and DefaultSettings.apiSuccess == False:
            logging.info("Retrying to call Api for getting urls")
            DefaultSettings.getEnterPoint(self.PARAMS["BASE_URL"] ,self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"] )

        # code for checking s_run_id present in db 
        if "RUN_ID" in self.PARAMS:
            print("************Trying to check If s_run_id is present in DB*****************")
            response =  dataUpload.checkingData(self.s_run_id, self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])
            if response == "failed":
                print("************s_run_id not present in DB Trying to call Post*****************")
                dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])

        elif ("USERNAME" in self.PARAMS.keys() and "BRIDGE_TOKEN" in self.PARAMS.keys()):
            dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])
            ### first try to rerun the data
            if dataUpload.suite_uploaded == False:
                print("------Retrying to Upload Suite Data------")
                dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])
        
        self.makeOutputFolder()
        self.start()
        #trying second rerun of base url api in case of api failure
        if self.PARAMS.get("BASE_URL", None) and DefaultSettings.apiSuccess == False:
                logging.info("Second Time Retrying to call Api for getting urls")
                DefaultSettings.getEnterPoint(self.PARAMS["BASE_URL"] ,self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"] )
        ### Trying to reupload suite data
        if("USERNAME" in self.PARAMS.keys() and "BRIDGE_TOKEN" in self.PARAMS.keys()) :
            if dataUpload.suite_uploaded == False:
                print("------Retrying to Upload Suite Data------")
                dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])

        ### checking if suite data is uploaded if true than retrying to upload testcase otherwise storing them in json file
        if dataUpload.suite_uploaded == True:
            jewelLink = DefaultSettings.getUrls('jewel-url')
            self.jewel = f'{jewelLink}/#/autolytics/execution-report?s_run_id={self.s_run_id}'
            if len(dataUpload.not_uploaded) != 0:
                print("------Trying again to Upload Testcase------")
                for testcase in dataUpload.not_uploaded:
                    dataUpload.sendTestcaseData(testcase, self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])
            failed_Utestcases = len(dataUpload.not_uploaded) 
            ### Creating file for unuploaded testcases
            if len(dataUpload.not_uploaded) != 0:
                if dataUpload.flag == True:
                    logging.warning("Testcase may be present with same tc_run_id in database")
                listToStr = ',\n'.join(map(str, dataUpload.not_uploaded))
                unuploaded_path = os.path.join(self.ouput_folder, "Unploaded_testCases.json")
                with open(unuploaded_path,'w') as w:
                    w.write(listToStr)
        self.updateSuiteData()
        suite_status = self.DATA.suite_detail.to_dict(orient="records")[0]["status"]
        testcase_analytics = self.DATA.suite_detail.to_dict(orient="records")[0]["testcase_analytics"]
        try:
            jira_email = self.PARAMS["JIRA_EMAIL"]
            jira_access_token = self.PARAMS["JIRA_ACCESS_TOKEN"]
            jira_title = self.PARAMS.get("JIRA_TITLE", None)
            jira_project_id = self.PARAMS.get("JIRA_PROJECT_ID", None)
            jira_workflow = self.PARAMS.get("JIRA_WORKFLOW", None)
        except Exception as e:
            pass

        ### checking if suite post/get request is successful to call put request otherwise writing suite data in a file
        if dataUpload.suite_uploaded == True:
            if("USERNAME" in self.PARAMS.keys() and "BRIDGE_TOKEN" in self.PARAMS.keys()):
                jira_id = jiraIntegration(self.s_run_id, suite_status, testcase_analytics, self.jewel, jira_email, jira_access_token, jira_title, jira_project_id, jira_workflow)
                if jira_id is not None:
                    self.DATA.suite_detail.at[0, "miscData"].append({"Jira_id": jira_id})
                dataUpload.sendSuiteData(self.DATA.toSuiteJson(), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"], mode="PUT")
        else:
            if not self.PARAMS.get("BASE_URL", None):
                logging.warning("Maybe username or bridgetoken is missing or wrong thus data is not uploaded in db.")
            dataUpload.suite_data.append(self.DATA.toSuiteJson())
            listToStr = ',\n'.join(map(str, dataUpload.suite_data))
            unuploaded_path = os.path.join(self.ouput_folder, "Unuploaded_suiteData.json")
            with open(unuploaded_path,'w') as w:
                w.write(listToStr)
        self.repJson, output_file_path = TemplateData().makeSuiteReport(self.DATA.getJSONData(), self.testcase_data, self.ouput_folder)
        TemplateData().repSummary(self.repJson, output_file_path, self.jewel, failed_Utestcases, unuploaded_path)

    def makeOutputFolder(self):
        """
        make outputFolder for report named as gempyp_reports in user home directory if not given by the user and makes log fplder for log files
        if given by user than set user given path for reports file   
        """

        logging.info("---------- Making output folders -------------")
        report_folder_name = f"{self.project_name}_{self.project_env}"
        if self.report_name:
            report_folder_name = report_folder_name + f"_{self.report_name}"
        date = datetime.now().strftime("%Y_%b_%d_%H%M%S_%f")
        report_folder_name = report_folder_name + f"_{date}"
        if "OUTPUT_FOLDER" in self.PARAMS and self.PARAMS["OUTPUT_FOLDER"]:
            self.ouput_folder = os.path.join(
                self.PARAMS["OUTPUT_FOLDER"], report_folder_name
            )
        else:
            home = str(Path.home())
            self.ouput_folder = os.path.join(
                home, "gempyp_reports", report_folder_name
            )

        os.makedirs(self.ouput_folder)
        self.testcase_folder = os.path.join(self.ouput_folder, "testcases")
        os.makedirs(self.testcase_folder)
        self.testcase_log_folder = os.path.join(self.ouput_folder, "logs")
        os.environ['TESTCASE_LOG_FOLDER'] = self.testcase_log_folder
        os.makedirs(self.testcase_log_folder)

    def setUP(self, config: Type[AbstarctBaseConfig]):
        """
        assigning values to some attributes which will be used in method makeSuiteDetails
        """
        self.PARAMS = config.getSuiteConfig()
        #checking if url is present in file and calling get api
        if self.PARAMS.get("BASE_URL", None):
            DefaultSettings.getEnterPoint(self.PARAMS["BASE_URL"] ,self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"] )
        self.CONFIG = config
        self.testcase_data = {}
        self.total_runable_testcase = config.total_yflag_testcase
        self.machine = platform.node()
        if("USERNAME" in self.PARAMS):
            self.user = self.PARAMS["USERNAME"]
        else:
            self.user=getpass.getuser()
        self.current_dir = os.getcwd()
        self.platform = platform.system()
        self.start_time = datetime.now(timezone.utc)
        self.project_name = self.PARAMS["PROJECT"]
        self.report_name = self.PARAMS.get("REPORT_NAME")
        self.project_env = self.PARAMS["ENV"]
        self.unique_id = self.PARAMS["UNIQUE_ID"]
        self.user_suite_variables = self.PARAMS["SUITE_VARS"]
        # self.report_info = self.PARAMS.get("REPORT_INFO")

        #add suite_vars here 

    def parseMails(self):
        """
        to get the mail from the configData
        """
        if("MAIL" in self.PARAMS.keys()):
            self.mail = common.parseMails(self.PARAMS["MAIL"])
            print(self.mail)

    def makeSuiteDetails(self):
        """
        making suiteDetails dictionary and assign it to DATA.suiteDetail 
        """
        if "RUN_ID" in self.PARAMS:
            self.s_run_id = self.PARAMS["RUN_ID"]
        else:
            if not self.unique_id:
                self.unique_id = uuid.uuid4()
            self.s_run_id = f"{self.project_name}_{self.project_env}_{self.unique_id}"
            self.s_run_id = self.s_run_id.upper()
        logging.info("S_RUN_ID: {}".format(self.s_run_id))
        run_mode = "LINUX_CLI"
        if os.name == 'nt':
            run_mode = "WINDOWS"
        suite_details = {
            "s_run_id": self.s_run_id,
            "s_start_time": self.start_time,
            "s_end_time": None,
            "status": status.EXE.name,
            "project_name": self.project_name,
            "run_type": "ON DEMAND",
            "report_name": self.report_name,  # earlier it was report info
            "user": self.user,
            "env": self.project_env,
            "machine": self.machine,
            "initiated_by": self.user,
            "run_mode": run_mode,
            "miscData": [],
            "expected_testcases": self.total_runable_testcase,
            "testcase_analytics": None,
            "framework_name": "GEMPYP",  # later this will be dynamic( GEMPYP-PR for pyprest)
        }
        self.DATA.suite_detail = self.DATA.suite_detail.append(
            suite_details, ignore_index=True
        )

    def start(self):

        """
         check the mode and start the testcases accordingly e.g.optimize,parallel
        """
        print("here")
        try:
            if self.CONFIG.getTestcaseLength() <= 0:
                raise Exception("no testcase found to run")

            if self.PARAMS["MODE"].upper() == "SEQUENCE":
                self.startSequence()
            elif self.PARAMS["MODE"].upper() == "OPTIMIZE" or self.PARAMS.get("MODE", None) is None:
                self.startParallel()
            else:
                raise TypeError("mode can only be sequence or optimize")

        except Exception as e:
            logging.error(traceback.format_exc())
            try:
                self.DATA.suite_detail.at[0, "miscData"].append({"REASON OF FAILURE": str(e)})
                self.updateSuiteData()
                print(self.DATA.suite_detail)
            except Exception as err:
                logging.error(traceback.format_exc())
                print(err)
            dataUpload.sendSuiteData((self.DATA.toSuiteJson()), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])
            # need to add reason of failure of the suite in misc


    def updateSuiteData(self):
        """
        updates the suiteData after all the runs have been executed
        """

        # get the status count of the status
        status_dict = self.DATA.testcase_details["status"].value_counts().to_dict()
        total = sum(status_dict.values())
        status_dict["TOTAL"] = total
        unsorted_dict = status_dict
        sorted_dict = self.totalOrder(unsorted_dict)
        status_dict = sorted_dict
        # status_dict = dict( sorted(status_dict.items(), key=lambda x: x[0].lower(), reverse=True) )
        Suite_status = status.FAIL.name

        # based on the status priority
        for s in status:
            if status_dict.get(s.name, 0) > 0:
                Suite_status = s.name
                break
        stop_time = (
            self.DATA.testcase_details["end_time"].sort_values(ascending=False).iloc[0]
        )
        self.DATA.suite_detail.at[0, "status"] = Suite_status
        self.DATA.suite_detail.at[0, "s_end_time"] = stop_time
        self.DATA.suite_detail.at[0, "testcase_analytics"] = status_dict
        # self.DATA.suite_detail.at[0, "duration"] = common.findDuration(self.start_time, stop_time)  

    def startSequence(self):
        """
        start calling executoryFactory() for each testcase one by one according to their dependency
        at last of each testcase calls the update_df() 
        """

        for testcases in self.getDependency(self.CONFIG.getTestcaseConfig()):
            for testcase in testcases:
                data = self.getTestcaseData(testcase['NAME'])
                log_path = os.path.join(self.testcase_log_folder,
                data['config_data'].get('NAME')+'_'+self.CONFIG.getSuiteConfig()['UNIQUE_ID'] + '.log')
                custom_logger = my_custom_logger(log_path)
                data['config_data']['log_path'] = log_path
                conn = None
                output, error = executorFactory(data,conn, custom_logger)
                if error:
                    custom_logger.error(
                        f"Error occured while executing the testcase: {error['testcase']}"
                    )
                    custom_logger.error(f"message: {error['message']}")
                self.update_df(output, error)



    def startParallel(self):
        """
        start calling executorFactory for testcases in parallel according to their drependency 
        at last of each testcase calls the update_df()
        """
        
        pool = None
        try:
            
            # threads = self.PARAMS.get("THREADS", DefaultSettings.THREADS)
            # try:
            #     threads = int(threads)
            # except:
            #     threads = DefaultSettings.THREADS
            # pool = Pool(threads)
           
           
            for testcases in self.getDependency(self.CONFIG.getTestcaseConfig()):
                processes = []

        # create a list to keep connections
                parent_connections = []
                if len(testcases) == 0:
                    raise Exception("No testcase to run")
                pool_list = []
                for testcase in testcases:
                    # only append testcases whose dependency are passed otherwise just update the databasee
                    if self.isDependencyPassed(testcase):
                        pool_list.append(self.getTestcaseData(testcase.get("NAME")))
                    
                    else:

                        print("----------------here--------------------")
                        dependency_error = {
                            "message": "dependency failed",
                            "testcase": testcase["NAME"],
                            "category": testcase.get("CATEGORY", None),
                            "product_type": testcase.get("product_type", None),
                        }
                        # handle dependency error in json_data(update_df)
                        # update the testcase in the database with failed dependency
                        self.update_df(None, dependency_error)
       
                if len(pool_list) == 0:
                    continue
                print("*****************")
                print(pool_list)
                for testcase in pool_list:
                    parent_conn, child_conn = Pipe()
                    parent_connections.append(parent_conn)

            # create the process, pass instance and connection
                    process = Process(target=executorFactory, args=(testcase, child_conn,))
                    processes.append(process) 
                # runs the testcase in parallel here
                # splitedSize = 4
                # a_splited = [processes[x:x+splitedSize] for x in range(0, len(processes), splitedSize)]
                instances_total = []
            
                # print(a_splited)
                # for i in a_splited:
                for process in processes:
                    process.start()
                for parent_connection in parent_connections:
                    instances_total.append(parent_connection.recv()[0])
                for process in processes:
                    process.join()
                    
                for row in instances_total:
                    if not row or len(row) < 2:
                        raise Exception(
                            "Some error occured while running the testcases"
                        )
                    output = row[0]
                    
                    error = row[1]
                    if error:
                        logging.error(
                            f"Error occured while executing the testcase: {error['testcase']}"
                        )
                        logging.error(f"message: {error['message']}")
                    self.update_df(output, error)
                if process:
                    process.join()
        except Exception:
            logging.error(traceback.format_exc())
        finally:
            if process:
                process.join()


    def update_df(self, output: List, error: Dict):

        """
        updates the testcase data in the dataframes of testData.py
        also upload testcasedata to db
        
        """
        try:
            if error:
                output = self.getErrorTestcase(
                    error["message"],
                    error["testcase"],
                    error.get("category"),
                    error.get("product_type"),
                    error.get('log_path', None)
                )
                output = [output]
            unsorted_dict = output[0]['json_data']['metaData'][2]
            sorted_dict = self.totalOrder(unsorted_dict)
            output[0]['json_data']['metaData'][2] = sorted_dict
            for i in output:

                i["testcase_dict"]["steps"] = i["json_data"]["steps"]
                
                testcase_dict = i["testcase_dict"]
                try:
                    """ update suite vars here from testcase_dict["suite_variables"] append it in the suite vars of _config"""
    
                    self.user_suite_variables.update(i.get("suite_variables", {}))
                    
                    self.testcase_data[testcase_dict.get("tc_run_id")] = i["json_data"]
                except Exception as e:
                    logging.error(e)

                self.DATA.testcase_details = self.DATA.testcase_details.append(
                    testcase_dict, ignore_index=True
                )
                self.updateTestcaseMiscData(
                    i["misc"], tc_run_id=testcase_dict.get("tc_run_id")
                )
                if("USERNAME" in self.PARAMS.keys() and "BRIDGE_TOKEN" in self.PARAMS.keys()):
                    dataUpload.sendTestcaseData((self.DATA.totestcaseJson(testcase_dict.get("tc_run_id").upper(), self.s_run_id)), self.PARAMS["BRIDGE_TOKEN"], self.PARAMS["USERNAME"])
        except Exception as e:
            logging.error("in update_df: {e}".format(e=e))

    def getErrorTestcase(
        self,
        message: str,
        testcase_name: str,
        category: str = None,
        product_type: str = None,
        log_path: str = None
    ) -> Dict:
        """
        store the data of failed testcase and return it as a dict to update_df
        take message for error as input
        """

        result = {}
        testcase_dict = {}
        misc = {}
        if not self.unique_id:
            self.unique_id = uuid.uuid4()
        tc_run_id = f"{testcase_name}_{self.project_env}_{self.unique_id}"
        tc_run_id = tc_run_id.upper()
        testcase_dict["tc_run_id"] = tc_run_id
        testcase_dict["status"] = status.FAIL.name
        testcase_dict["start_time"] = datetime.now(timezone.utc)
        testcase_dict["end_time"] = datetime.now(timezone.utc)
        testcase_dict["name"] = testcase_name
        testcase_dict["ignore"] = False
        if category:
            testcase_dict["category"] = category
        testcase_dict["log_file"] = log_path
        testcase_dict["result_file"] = None
        testcase_dict["user"] = self.user
        testcase_dict["machine"] = self.machine
        # testcase_dict["response_time"]="{0:.{1}f} sec(s)".format((testcase_dict["end_time"]-testcase_dict["start_time"]).total_seconds(),2)
        if product_type:
            testcase_dict["product_type"] = product_type

        result["testcase_dict"] = testcase_dict

        misc["REASON OF FAILURE"] = message

        result["misc"] = misc

        return result

    def updateTestcaseMiscData(self, misc: Dict, tc_run_id: str):
        """
        updates the misc data for the testcases in testData.py
        accept miscellaneous rows and tc_run_id as parameters
        """
        misc_list = []

        for misc_data in misc:
            temp = {}
            # storing all the key in upper so that no duplicate data is stored
            temp["key"] = misc_data.upper()
            temp["value"] = misc[misc_data]
            temp["run_id"] = tc_run_id
            temp["table_type"] = "TESTCASE"
            misc_list.append(temp)

        self.DATA.misc_details = self.DATA.misc_details.append(
            misc_list, ignore_index=True
        )

    def getTestcaseData(self, testcase: str) -> Dict:
        """
        taking argument as the testcase name and  return dictionary containing information about testCase
        """
        data = {}
        list_subtestcases=[]
        data["config_data"] = self.CONFIG.getTestcaseData(testcase)
        if("SUBTESTCASES" in data["config_data"].keys()):
            for key1 in data["config_data"]["SUBTESTCASES"].split(","):
                list_subtestcases.append(self.CONFIG.getSubTestcaseData(key1))
            data["config_data"]["SUBTESTCASES_DATA"]=list_subtestcases
        data["PROJECT_NAME"] = self.project_name
        data["ENV"] = self.project_env
        if(self.project_env.upper() in self.PARAMS.keys()):
            data[self.project_env.upper()]=self.PARAMS[self.project_env.upper()]
        data["S_RUN_ID"] = self.s_run_id
        data["USER"] = self.user
        data["MACHINE"] = self.machine
        data["OUTPUT_FOLDER"] = self.testcase_folder
        data["SUITE_VARS"] = self.user_suite_variables
        return data

    

    def getDependency(self, testcases: Dict):
        """
        yields the testcases with least dependncy first
        Reverse toplogical sort
        accept all testcases dictionary as arguments
        """
        adj_list={}
        for key,value in testcases.items():
                adj_list[key]=list(set(list(value.get("DEPENDENCY","").split(",")))  - set([""]))       

        for key, value in adj_list.items():
            new_list = []
            for testcase in value:

                testcase = testcase.split(":")
                if len(testcase) > 1:
                    new_list.append(testcase[1])
                else:
                    new_list.append(testcase[0])

            adj_list[key] = set(new_list)
        
        while adj_list:
            """
            return testcases that doesn't depend on other testcase
            """
            top_dep = set(
                i for dependents in list(adj_list.values()) for i in dependents
            ) - set(adj_list.keys())
            top_dep.update(key for key, value in adj_list.items() if not value)
        
            if not top_dep:
                logging.critical(
                    "circular dependency found please remove the cirular dependency"
                )
                logging.debug("possible testcase with circular dependencies")
                sys.exit(1)

            adj_list = {key: value - top_dep for key, value in adj_list.items() if value}
            result = []
            for key in testcases:
                if key in top_dep:
                    result.append(testcases[key])
            yield result

   

    def isDependencyPassed(self, testcase: Dict) -> bool:
        """
        cheks if the dependency is passed for the testcase or not
        """

        # split on ','
        listOfTestcases=[]
        listOfTestcases=list(set(list(testcase.get("DEPENDENCY", "").split(","))) - set([""]))
        for dep in listOfTestcases:

                    dep_split = list(dep.split(":"))
                    if len(dep_split) == 1:
                        # NAME to name, to_list()
                        if dep_split[0] not in self.DATA.testcase_details["name"].to_list():
                            return False

                    else:
                        if dep_split[0].upper() == "P":
                            if dep_split[1] not in self.DATA.testcase_details["name"].to_list():
                                return False
                            # way to parsing the df    
                            if ((self.DATA.testcase_details[self.DATA.testcase_details["name"] == dep_split[1]]['status'].iloc[0]) != status.PASS.name):
                                return False

                        if dep_split[0].upper() == "F":
                            if dep_split[1] not in self.DATA.testcase_details["name"].to_list():
                                return False
                            if (
                                (self.DATA.testcase_details[self.DATA.testcase_details["name"] == dep_split[1]]['status'].iloc[0])
                                != status.FAIL.name
                            ):
                                return False

        return True

    ### Function for sending total, pass, fail in order
    def totalOrder(self, unsorted_dict):
        
        prio_list = ['TOTAL', 'PASS', 'FAIL']
        sorted_dict = {}
        for key in prio_list:
            if key in unsorted_dict :
                sorted_dict[key] = unsorted_dict[key]
                unsorted_dict.pop(key)
            elif key == "PASS" or key == 'FAIL':
                sorted_dict[key] = 0
        sorted_dict.update(unsorted_dict)

        return sorted_dict
