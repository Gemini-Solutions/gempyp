import uuid
from gempyp.libs.gem_s3_common import upload_to_s3, create_s3_link
from gempyp.config import DefaultSettings
import mysql.connector
import os
import uuid
import configparser
from typing import Dict
import pandas as pd
from gempyp.engine.baseTemplate import TestcaseReporter as Base
from gempyp.libs.common import moduleImports
from gempyp.libs.enums.status import status
from gempyp.libs.common import readPath
from gempyp.dv.dvReporting import writeToReport
import traceback
import pandas as pd
import logging
import math
import numpy
import pg8000
from gempyp.dv.dvObj import DvObj
from gempyp.libs.common import download_common_file,get_reason_of_failure
from gempyp.engine.runner import getError
from gempyp.libs import common
from gempyp.dv.dvDataframe import Dataframe
# from gempyp.dv.dvCompare import df_compare
from gempyp.dv.dfOperations import dateFormatHandling, columnCompare, skipColumn
import re
import json
import ast
from gempyp.dv.dataCompare import df_compare


class DvRunner(Base):

    def __init__(self, data):

        self.data = data
        self.configData: Dict = self.data.get("config_data")
        self.configData['USERNAME'] = self.data["SUITE_VARS"]["username"]
        self.configData['BRIDGE_TOKEN'] = self.data["SUITE_VARS"]["bridge_token"] 
        self.logger = data["config_data"]["LOGGER"] if "LOGGER" in data["config_data"].keys(
        ) else logging
        self.logger.info(
            "---------------------Inside DV FRAMEWORK------------------------")
        self.logger.info(
            f"-------Executing testcase - \"{self.data['config_data']['NAME']}\"---------")
        if data.get("default_urls", None):
            # only for optimized mode, urls not shared between processes
            DefaultSettings.urls.update(data.get("default_urls"))
        self.setVars()
        self.logger.info(
            "--------------------Report object created ------------------------")
        self.reporter = Base(project_name=self.project,
                            testcase_name=self.tcname)
        self.reporter.logger = self.logger
        self.configData['REPORT_LOCATION'] = self.data.get("REPORT_LOCATION",None)

    def dvEngine(self):

        self.sourceCred = None
        self.targetCred = None
        try:
            try:
                if "SOURCE_DB" or "TARGET_DB" in self.configData:
                    if "DB_CONFIG_PATH" in self.configData:
                        configPath = self.configData["DB_CONFIG_PATH"]
                        self.configur = configparser.RawConfigParser()
                        config = readPath(configPath)
                        self.configur.read(config)
                    else:
                        self.configur = None
            except Exception as e:
                self.reporter.addRow(
                    "Config File", "Path is not Correct", status.ERR)
                raise Exception(e)
            if 'SOURCE_DB' or 'TARGET_DB' in self.configData:
                self.dbConnParser()

            if "KEYS" in self.configData:
                self.keys = self.configData["KEYS"].split(',')
                self.reporter.addMisc("KEYS", ", ".join(self.keys))
            else:
                self.reporter.addRow(
                    "Checking Keys", "User Given Keys Tag not Found", status.ERR)
                raise Exception("User Given Keys not Found")

            obj = Dataframe()
            self.source_df, self.source_columns = Dataframe.getSourceDataFrame(
                obj, self.data, self.logger, self.reporter, self.sourceCred)
            self.target_df, self.target_columns = Dataframe.getTargetDataframe(
                obj, self.data, self.logger, self.reporter, self.targetCred)
            
            if "BEFORE_FILE" in self.configData:
                self.beforeMethod()

            df_compare(
                self.source_df, self.target_df, self.keys, self.reporter, self.configData)
            
            # self.writeExcel(value_dict, key_dict, keys_length, duplicate_keys_df, dup_keys_length)
            self.reporter.finalizeReport()
            output = writeToReport(self)
            return output, None
        except Exception as e:
            self.reporter.addMisc(
                    "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))
            self.logger.error(str(e))
            traceback.print_exc()
            output = writeToReport(self)
            return output, None

    def dbConnParser(self):
        """checking db type and fetching credentials or connection details accordingly"""
        try:
            if 'SOURCE_DB' in self.configData:
                if 'SOURCE_CONN' in self.configData: 
                    is_dict = True
                    try:
                        db_details = ast.literal_eval(self.configData["SOURCE_DB"])
                    except Exception:
                        is_dict = False
                    if is_dict == True:
                        db_type = db_details.get('type')
                    else:
                        db_type = self.configData["SOURCE_DB"]
                    if db_type.lower() == 'custom':
                        self.sourceCred = self.configData['SOURCE_CONN']
                    else:
                        if re.search("^{.*}$", self.configData["SOURCE_CONN"]):
                            self.sourceCred = eval(self.configData["SOURCE_CONN"])
                        else:
                            self.logger.info("----Parsing the Config File For Source Connections----")
                            self.sourceCred = dict(self.configur.items(
                                self.configData["SOURCE_CONN"]))
                            self.sourceCred=self.parseConfigDict(self.sourceCred)
            
            if 'TARGET_DB' in self.configData:
                if 'TARGET_CONN' in self.configData:
                    is_dict = True
                    try:
                        db_details = ast.literal_eval(self.configData["TARGET_DB"])
                    except Exception:
                        is_dict = False
                    if is_dict == True:
                        db_type = db_details.get('type')
                    else:
                        db_type = self.configData["TARGET_DB"]
                    
                    if db_type.lower() == 'custom':
                        self.targetCred = self.configData['TARGET_CONN']
                    else:
                        if re.search("^{.*}$", self.configData["TARGET_CONN"]):
                            self.targetCred = eval(self.configData["TARGET_CONN"])
                        else:
                            self.targetCred = dict(self.configur.items(
                                self.configData["TARGET_CONN"]))
                            self.targetCred=self.parseConfigDict(self.targetCred)

            if self.configur != None:
                self.reporter.addRow(
                    "Parsing DB Conf", "Parsing of DB config is Successfull", status.PASS)
        except Exception as e:
            self.reporter.addRow(
                "Parsing DB Conf", "Exception Occurred", status.ERR)
            self.reporter.addMisc(
                "REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))
            raise Exception(e)

    def setVars(self):
        """
        For setting variables like testcase name, output folder etc.
        """
        self.data["config_data"]=self.parseConfig(self.data["config_data"])
        self.default_report_path = os.path.join(os.getcwd(), "pyprest_reports")

        self.data["REPORT_LOCATION"] = self.data.get("REPORT_LOCATION", self.default_report_path)
        if self.data["REPORT_LOCATION"].strip(" ") == "":
            self.data["REPORT_LOCATION"] = self.default_report_path

        self.project = self.data["PROJECT_NAME"]
        self.tcname = self.data["config_data"]["NAME"]
        self.env = self.data["ENVIRONMENT"]
        self.category = self.data["config_data"].get("CATEGORY", None)

    
    def beforeMethod(self):
        """This function
        -checks for the before file tag
        -stores package, module,class and method
        -runs before method if found
        -takes all the data from before method and updates the self object"""

        # check for before_file
        self.logger.info("CHECKING FOR BEFORE FILE___________________________")

        file_str = self.data["config_data"].get("BEFORE_FILE", "")
        if not file_str or file_str == "" or file_str == " ":
            self.logger.info(
                "BEFORE FILE NOT FOUND___________________________")
            self.reporter.addRow(
                "Searching for Before_File steps", "No Before File steps found", status.INFO)

            return
        self.reporter.addRow("Searching for Before_File steps",
                            "Searching for Before File", status.INFO)

        file_name = file_str.split("path=")[1].split(",")[0]
        if "CLASS=" in file_str.upper():
            class_name = file_str.split("class=")[1].split(",")[0]
        else:
            class_name = ""
        if "METHOD=" in file_str.upper():
            method_name = file_str.split("method=")[1].split(",")[0]
        else:
            method_name = "before"

        self.logger.info("Before file path:- " + file_name)
        self.logger.info("Before file class:- " + class_name)
        self.logger.info("Before file mthod:- " + method_name)
        try:
            file_path = download_common_file(
                file_name, self.data.get("SUITE_VARS", None))
            file_obj = moduleImports(file_path)
            self.logger.info("Running before method")
            obj_ = file_obj
            before_obj = DvObj(
                project=self.project,
                source_df=self.source_df,
                target_df=self.target_df,
                source_columns=self.source_columns,
                target_columns=self.target_columns,
                keys=self.keys,
                env=self.env,
                reporter=self.reporter 
            )
            if class_name != "":
                obj_ = getattr(file_obj, class_name)()
            fin_obj = getattr(obj_, method_name)(before_obj)
            self.extractBeforeObj(fin_obj)

        except Exception as e:
            self.logger.info(traceback.format_exc())
            self.reporter.addRow(
                "Executing Before method", f"Some error occurred while searching for before method- {str(e)}", status.ERR)

    def extractBeforeObj(self, obj):
        """To ofload the data from pyprest obj helper, assign the values back to self object"""

        self.reporter = obj.object
        self.project = obj.project
        self.source_columns = obj.source_columns
        self.target_columns = obj.target_columns
        self.source_df = obj.source_df
        self.target_df = obj.target_df
        self.keys = obj.keys
        self.env = obj.env
        self.reporter = obj.reporter
    
    def parseConfig(self,config):
        pattern = r"ENV.([a-zA-Z0-9_]+)"
        for key in config.keys():
            value=config.get(key)
            if(type(value)!=logging.Logger):
                if re.search("mysql.connector.connect",value) or re.search("^{",value):
                    config[key] = re.sub(pattern, lambda match: f"'{os.environ.get(match.group(1), '')}'", value)
                else:
                    if("ENV." in value):
                        config[key]=os.environ.get(value.replace("ENV.",""))
        return config
    
    def parseConfigDict(self,conf):
        for key in conf.keys():
            if("ENV." in conf.get(key) and os.environ.get(conf.get(key).replace("ENV.",""))):
                conf[key]=os.environ.get(conf.get(key).replace("ENV.",""))
        return conf
                
