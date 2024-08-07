import uuid
from gempyp.libs.gem_s3_common import uploadToS3, create_s3_link
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
from gempyp.dv.dvCompare import df_compare
from gempyp.dv.dfOperations import dateFormatHandling, columnCompare, skipColumn
import re
import json
import ast


class DvRunner(Base):

    def __init__(self, data):

        self.data = data
        self.configData: Dict = self.data.get("config_data")
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
                    "Config file", "Path is not correct", status.ERR)
                raise Exception(e)
            if 'SOURCE_DB' or 'TARGET_DB' in self.configData:
                self.dbConnParser()

            if "KEYS" in self.configData:
                self.keys = self.configData["KEYS"].split(',')
                self.reporter.addMisc("KEYS", ", ".join(self.keys))
            else:
                self.reporter.addRow(
                    "Checking keys", "User given keys tag not found", status.ERR)
                raise Exception("User given keys not found")

            obj = Dataframe()
            self.source_df, self.source_columns = Dataframe.getSourceDataFrame(
                obj, self.data, self.logger, self.reporter, self.sourceCred)
            self.target_df, self.target_columns = Dataframe.getTargetDataframe(
                obj, self.data, self.logger, self.reporter, self.targetCred)
            
            if "BEFORE_FILE" in self.configData:
                self.beforeMethod()
            # for columns mapping
            if "COLUMN_MAP" in self.configData:
                self.target_df.rename(columns=eval(
                    self.configData["COLUMN_MAP"]), inplace=True)
                self.target_columns = list(self.target_df.columns)
            self.matchKeys(self.source_columns, "SOURCE")
            self.matchKeys(self.target_columns, "TARGET")

            if 'SKIP_COLUMN' in self.configData:
                self.source_df, self.target_df = skipColumn(self.configData.get('SKIP_COLUMN'),self.source_df,self.target_df,self.keys,self.reporter)
                self.source_columns = list(self.source_df.columns)
                self.target_columns = list(self.target_df.columns)
            #calling getDuplicatekeysDf function to get dataframe of duplicate keys 
            source_duplicates_df, src_dup_len = self.getDuplicateKeysDf(self.source_df, "SOURCE")
            target_duplicates_df, tgt_dup_len = self.getDuplicateKeysDf(self.target_df, "TARGET")
            dup_keys_length = src_dup_len + tgt_dup_len
            duplicate_keys_df = pd.concat([source_duplicates_df , target_duplicates_df ], axis=0, ignore_index=True)

            if self.source_columns == self.target_columns:
                pass
            else:
                self.logger.info(
                    "--------Same Column not Present in Both Table--------")
                self.reporter.addRow(
                    "Same columns in table", "Not found", status.ERR)
                raise Exception("Same Columns Not Found")

            """deleting duplicates from df and keeping last ones"""
            self.logger.info("Removing Duplicates Rows")
            self.source_df.drop_duplicates(
                subset=self.keys, keep='last', inplace=True)
            self.target_df.drop_duplicates(
                subset=self.keys, keep='last', inplace=True)
            
            #calling compare column
            if "COMPARE_COLUMN" in self.configData:
                compare_column = self.configData.get("COMPARE_COLUMN",'').split(',')
                self.source_df, self.target_df = columnCompare(self.source_df, self.target_df, self.keys, compare_column)
            # hadling case insensitivity
            if 'MATCH_CASE' in self.configData:
                self.matchCase()

            # date format handling
            self.source_df, self.target_df = dateFormatHandling(self.source_df, self.target_df)
            
            #checking column compare
            value_dict, key_dict, keys_length = df_compare(
                self.source_df, self.target_df, self.keys, self.logger, self.reporter, self.configData)
            
            self.writeExcel(value_dict, key_dict, keys_length, duplicate_keys_df, dup_keys_length)
            self.reporter.finalizeReport()
            output = writeToReport(self)
            return output, None
        except Exception as e:
            self.reporter.addMisc(
                    "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))
            self.reporter.addRow("Stopping execution", get_reason_of_failure(traceback.format_exc(), e), status.ERR)
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
                    "Parsing db conf", "Parsing of db config is successful", status.PASS)
        except Exception as e:
            self.reporter.addRow(
                "Parsing db conf", "Exception occurred", status.ERR)
            self.reporter.addMisc(
                "REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))
            raise Exception(e)

    def matchKeys(self, columns, db):

        try:
            self.logger.info(f"Matching Keys in {db} DB")
            key = []
            for i in self.keys:
                if i not in columns:
                    key.append(i)
            if len(key) == 0:
                self.reporter.addRow(
                    f"Matching given keys in {db}", f"Keys are present in {db}", status.PASS)
                self.logger.info(f"Given Keys are Present in {db} DB")
            else:
                raise (f"Keys are not Present in {db}")
        except Exception as e:
            keyString1 = ", ".join(key)
            self.reporter.addRow(
                f"Matching given keys in {db}", "Keys: " + keyString1 + f" are not present in {db}db", status.ERR)
            self.logger.info("------Given Keys are not present in DB------")
            raise Exception("Keys not Present in DB")

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

    def writeExcel(self, valDict, keyDict, keys_length, duplicate_keys_df, dup_keys_len):

        try:
            logging.info("----------in write excel---------")
            key_check = len(keyDict["Reason-of-Failure"])
            value_check = len(valDict["Reason-of-Failure"])
            self.logger.info("In write Excel Function")
            outputFolder = self.data['REPORT_LOCATION']

            unique_id = uuid.uuid4()
            excelPath = os.path.join(
                outputFolder, self.configData['NAME']+str(unique_id)+'.csv')
            excel = os.path.join(
                ".", "testcases", self.configData['NAME']+str(unique_id)+'.csv')
            self.value_df = pd.DataFrame(valDict)
            self.keys_df = pd.DataFrame(keyDict)
            if "AFTER_FILE" in self.configData:
                self.afterMethod()
            if (key_check + value_check + dup_keys_len) == 0:
                self.reporter.addRow("Data validation report",
                                    "No misMatch value found", status=status.PASS)
                self.logger.info("----No MisMatch Value Found----")
            else:
                self.logger.info("----Adding Data to Excel----")
                # with pd.ExcelWriter(excelPath) as writer1:
                    # if key_check == 0:
                    #     pass
                    # else:
                    #     self.keys_df.to_excel(
                    #         writer1, sheet_name='key_difference', index=False)
                    # if value_check == 0:
                    #     pass
                    # else:
                    #     self.value_df.to_excel(
                    #         writer1, sheet_name='value_difference', index=False)
                df = pd.concat([self.value_df, self.keys_df, duplicate_keys_df ], axis=0, ignore_index=True)
                df_columns = set(df.columns)
                fixed_columns = {"Column-Name","Source-Value","Target-Value","Reason-of-Failure"}
                diff_columns = df_columns - fixed_columns
                new_order = list(diff_columns)+["Column-Name","Source-Value","Target-Value","Reason-of-Failure"]
                df = df[new_order]
                df.to_csv(excelPath, index=False,header=True)
                print(excelPath)
                s3_url = None
                try:
                    s3_url = uploadToS3(DefaultSettings.urls["data"].get("pre-signed",None), bridge_token=self.data["SUITE_VARS"]
                                            ["bridge_token"], tag="protected", username=self.data["SUITE_VARS"]["username"], file=excelPath,s_run_id=self.data.get("S_RUN_ID"))[0]
                except Exception as e:
                    print(traceback.print_exc())
                    logging.warn(e)
                if not s3_url:
                    self.reporter.addRow("Data validation report", f"Matched keys: {keys_length['common_keys']}, Keys only in source: {keys_length['keys_only_in_src']}, Keys only in target: {keys_length['keys_only_in_tgt']}, Mismatched cells: {value_check}, Duplicate keys: {dup_keys_len}, DV result file:", status=status.FAIL,Attachment=[excelPath])
                else:
                    self.reporter.addRow("Data Validation Report", f"Matched keys: {keys_length['common_keys']}, Keys only in source: {keys_length['keys_only_in_src']}, Keys only in target: {keys_length['keys_only_in_tgt']}, Mismatched cells: {value_check}, Duplicate keys: {dup_keys_len}, DV result file:", status=status.FAIL,Attachment=[s3_url])

                self.reporter.addMisc("REASON OF FAILURE", str(
                    f"Mismatched Keys: {key_check},Mismatched Cells: {value_check}"))
            self.reporter.addMisc("common Keys", str(keys_length['common_keys']))
            self.reporter.addMisc("Keys Only in Source",
                                str(keys_length['keys_only_in_src']))
            self.reporter.addMisc("Keys Only In Target",
                                str(keys_length['keys_only_in_tgt']))
            self.reporter.addMisc("Mismatched Cells", str(value_check))
        except Exception as e:
            self.reporter.addMisc(
                    "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))
            self.reporter.addRow("Writing data into csv","Exception occured",status.ERR)

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
                "Searching for before file steps", "No before file steps found", status.INFO)

            return
        self.reporter.addRow("Searching for before file steps",
                            "Searching for before file", status.INFO)

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
                "Executing before method", f"Some error occurred while searching for before method- {str(e)}", status.ERR)

    def afterMethod(self):
        """This function
        -checks for the after file tag
        -stores package, module,class and method
        -runs after method if found
        -takes all the data from after method and updates the self object"""

        self.logger.info("CHECKING FOR AFTER FILE___________________________")

        file_str = self.data["config_data"].get("AFTER_FILE", "")
        if not file_str or file_str == "" or file_str == " ":
            self.logger.info("AFTER FILE NOT FOUND___________________________")
            self.reporter.addRow(
                "Searching for after file steps", "No file path found", status.INFO)
            return

        self.reporter.addRow("Searching for after file",
                            "Searching for file", status.INFO)

        file_name = file_str.split("path=")[1].split(",")[0]
        if "CLASS=" in file_str.upper():
            class_name = file_str.split("class=")[1].split(",")[0]
        else:
            class_name = ""
        if "METHOD=" in file_str.upper():
            method_name = file_str.split("method=")[1].split(",")[0]
        else:
            method_name = "after"
        self.logger.info("After file path:- " + file_name)
        self.logger.info("After file class:- " + class_name)
        self.logger.info("After file mthod:- " + method_name)
        try:
            file_path = download_common_file(
                file_name, self.data.get("SUITE_VARS", None))
            file_obj = moduleImports(file_path)
            self.logger.info("Running After method")
            obj_ = file_obj
            after_obj = DvObj(
                project=self.project,
                value_df=self.value_df,
                keys_df=self.keys_df,
                env=self.env,
                reporter=self.reporter 
            )
            if class_name != "":
                obj_ = getattr(file_obj, class_name)()
            fin_obj = getattr(obj_, method_name)(after_obj)
            self.extractAfterObj(fin_obj)
        except Exception as e:
            self.reporter.addRow(
                "Executing after method", f"Some error occurred while searching for after method- {str(e)}", status.ERR)

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

    def extractAfterObj(self, obj):

        self.reporter = obj.object
        self.project = obj.project
        self.value_df = obj.value_df
        self.keys_df = obj.keys_df
        self.env = obj.env
        self.reporter = obj.reporter

    def matchCase(self):
        try:
            columns = self.configData['MATCH_CASE'].split(',')
            for i in columns:
                self.source_df[i] = self.source_df[i].apply(str.lower)
                self.target_df[i] = self.target_df[i].apply(str.lower)
        except Exception as e:
            self.reporter.addRow("Trying to match case",common.get_reason_of_failure(traceback.format_exc(), e), status.ERR)
            raise e
        
    def getDuplicateKeysDf(self, df, type):

        self.logger.info("Checking Dulicates Keys")
        dup_df = df[df[self.keys].duplicated(keep=False)]

        dup_keys_df = dup_df[self.keys]
        dup_length = len(dup_keys_df)
        dup_keys_df.drop_duplicates(
                keep='last', inplace=True)
        dup_keys_df['Reason-of-Failure'] = f'Duplicate Key in {type}'
        if len(dup_keys_df['Reason-of-Failure']) > 0:
            self.reporter.addRow(f"Checking for duplicates keys in {type}",f"Found duplicate keys in {type}",status.FAIL)
        return dup_keys_df, dup_length
    
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
                
