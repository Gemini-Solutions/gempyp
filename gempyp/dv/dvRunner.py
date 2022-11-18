import mysql.connector
import os
from configparser import ConfigParser
from posixpath import split
from sqlite3 import connect
from typing import Dict
import pandas as pd
from pyparsing import originalTextFor
import mysql.connector
from gempyp.engine.baseTemplate import TestcaseReporter as Base
from gempyp.libs.enums.status import status
from gempyp.libs.common import readPath
from gempyp.dv.dvReporting import writeToReport
from telnetlib import STATUS
import traceback
from numpy import sort
import pandas as pd
import xlsxwriter
import logging
import math
import numpy
import pg8000

class DvRunner(Base):

    def __init__(self, data):
        
        self.data = data

        self.configData: Dict = self.data.get("config_data")
        self.logger = data["config_data"]["LOGGER"] if "LOGGER" in data["config_data"].keys() else logging

        self.logger.info("---------------------Inside DVM FRAMEWORK------------------------")

        self.logger.info(f"-------Executing testcase - \"{self.data['config_data']['NAME']}\"---------")
        # # set vars
        self.setVars()
        
        # # setting self.reporter object
        self.logger.info("--------------------Report object created ------------------------")
        self.reporter = Base(project_name=self.project, testcase_name=self.tcname)
        
    def dvEngine(self):
        
        try:
            column =[]
            try:
                configPath= self.configData["DB_CONFIG_PATH"]
                configur = ConfigParser()
                config = readPath(configPath)
                configur.read(config)
            except Exception as e:
                self.reporter.addRow("Config File","Path is not Correct",status.FAIL)
                traceback.print_exc()
                output = writeToReport(self)
                return output, None
            try:
                self.logger.info("----Parsing the Config File----")
                userCred ={"host":configur.get(self.configData["SOURCE_DB"],'host'),"dbName":configur.get(self.configData["SOURCE_DB"],'databaseName'),"userName":configur.get(self.configData["SOURCE_DB"],'userName'),"password":configur.get(self.configData["SOURCE_DB"],'password'),"port":configur.get(self.configData["SOURCE_DB"],'port')}
                targetCred ={"host":configur.get(self.configData["TARGET_DB"],'host'),"dbName":configur.get(self.configData["TARGET_DB"],'databaseName'),"userName":configur.get(self.configData["TARGET_DB"],'userName'),"password":configur.get(self.configData["TARGET_DB"],'password'),"port":configur.get(self.configData["TARGET_DB"],'port')} 
                self.reporter.addRow("Parsing DB Conf","Parsing of DB config is Successfull",status.PASS)
            except Exception as e:
                self.logger.error(str(e))
                traceback.print_exc()
                self.reporter.addRow("Parsing DB Conf","Exception Occurred",status.FAIL)
                output = writeToReport(self)
                self.addReasonOfFailure(traceback)
                return output, None
            self.keys = self.configData["KEYS"].split(',')
            self.reporter.addMisc("KEYS",", ".join(self.keys))
            # parsing row and connection row
            self.li1 = []
            self.li2 = []
            for i in self.keys:
                column.append(i)
                self.li1.append([])
                self.li2.append([])
            
            """connecting to sourceDB"""
            try:
                self.logger.info("----Connecting to SourceDB----")
                if self.configData["DATABASE"].lower() == 'mysql':
                    myDB = mysql.connector.connect(host= userCred['host'],user = userCred["userName"], password = userCred['password'],database= userCred['dbName'])
                elif self.configData["DATABASE"].lower() == 'postgresql':
                    myDB = pg8000.connect(host= userCred['host'],user = userCred["userName"], password = userCred['password'],database= userCred['dbName'], port = userCred['port'])
                self.reporter.addRow("Connection to SourceDB: "+ str(userCred["host"]),"Connection to SourceDB is Successfull",status.PASS)
                myCursor = myDB.cursor()
            except Exception as e:
                self.logger.error(str(e))
                self.reporter.addRow("Connection to SourceDB: "+ str(userCred["host"]),"Exception Occurred",status.FAIL)
                self.addReasonOfFailure(traceback)
                
            try:
                self.logger.info("----Executing the SourceSQL----")
                myCursor.execute(self.configData['SOURCE_SQL'])
                self.reporter.addRow("Executing Source SQL","Source SQL executed Successfull",status.PASS)
                sourceColumns = [i[0] for i in myCursor.description]
            except Exception as e:
                self.logger.error(str(e))
                self.reporter.addRow("Executing Source SQL","Exception Occurred",status.FAIL)
                output = writeToReport(self)
                self.addReasonOfFailure(traceback)
                return output, None
            sorKeys =[]
            try:
                for i in self.keys:
                    if i in sourceColumns:
                        continue
                    else:
                        sorKeys.append(i)
                if len(sorKeys) == 0:
                    self.reporter.addRow("Matching Given Keys in Source SQL","Keys are Present in SourceDB",status.PASS)
                else:
                    raise Exception
            except Exception:
                keyString1 = ", ".join(sorKeys)
                self.reporter.addRow("Matching Given Keys in Source SQL","Keys: " + keyString1 +" are not Present in SourceDB",status.FAIL)
                self.logger.info("------Given Keys are not present in DB------")
                self.addReasonOfFailure(traceback)
            results = myCursor.fetchall()
            db_1 = pd.DataFrame(results, 
                                columns=sourceColumns)
            myDB.close()
            
            """Connecting to TargetDB"""
            try:
                self.logger.info("----Connecting to TargetDB----")
                if self.configData["DATABASE"].lower() == 'mysql':
                    myDB1 = mysql.connector.connect(host= targetCred['host'],user = targetCred["userName"], password = targetCred['password'],database= targetCred['dbName'])
                elif self.configData["DATABASE"].lower() == 'postgresql':
                    myDB1 = pg8000.connect(host= targetCred['host'],user = targetCred["userName"], password = targetCred['password'],database= targetCred['dbName'],port= targetCred['port'])
                self.reporter.addRow("Connection to TargetDB: "+ str(targetCred['host']),"Connection to TargetDB is Successfull",status.PASS)
                myCur = myDB1.cursor()
            except Exception as e:
                self.logger.error(str(e))
                self.reporter.addRow("Connection to TargetDB: "+ str(targetCred["host"]),"Exception Occurred",status.FAIL)
                self.addReasonOfFailure(traceback)
            try:
                self.logger.info("----Executing the TargetSQL----")
                myCur.execute(self.configData['TARGET_SQL'])
                self.reporter.addRow("Executing Target SQL","Source SQL executed Successfull",status.PASS)
                targetColumns = [i[0] for i in myCur.description]
            except Exception as e:
                self.logger.error(str(e))
                self.reporter.addRow("Executing Target SQL","Exception Occurred",status.FAIL)
                output = writeToReport(self)
                self.addReasonOfFailure(traceback)
                return output, None
            tarKeys =[]
            try:
                for i in self.keys:
            
                    if i in targetColumns:
                        continue
                    else:
                        tarKeys.append(i)
                if len(tarKeys)==0:
                    self.reporter.addRow("Matching Given Keys in Target SQL","Keys are Present in TargetDB",status.PASS)
                else:
                    raise Exception
            except Exception:
                    keyString2 = ", ".join(tarKeys)
                    self.reporter.addRow("Matching Given Keys in Target SQL","Keys: " + keyString2 +" are not Present in TargetDB",status.FAIL)
                    self.addReasonOfFailure(traceback)
            try:
                if sourceColumns==targetColumns:
                    pass
                else:
                    raise Exception
            except Exception:
                self.reporter.addRow("Column in Table","Not Found",status.FAIL)
                self.logger.info("--------Same Column not Present in Both Table--------")
                output = writeToReport(self)
                self.addReasonOfFailure(traceback)
                return output, None
            result1 = myCur.fetchall()
            db_2 = pd.DataFrame(result1, 
                                columns=targetColumns)
            
    
            self.df_compare(db_1, db_2, self.keys)
            self.reporter.finalizeReport()
            output = writeToReport(self)
            return output, None
        except Exception as e:
            self.logger.error(str(e))
            traceback.print_exc()
            self.addReasonOfFailure(traceback)


    def setVars(self):
        """
        For setting variables like testcase name, output folder etc.
        """
        self.default_report_path = os.path.join(os.getcwd(), "pyprest_reports")
        self.data["OUTPUT_FOLDER"] = self.data.get("OUTPUT_FOLDER", self.default_report_path)
        if self.data["OUTPUT_FOLDER"].strip(" ") == "":
            self.data["OUTPUT_FOLDER"] = self.default_report_path
        self.project = self.data["PROJECT_NAME"]
        self.tcname = self.data["config_data"]["NAME"]
        self.env = self.data["ENV"]
        self.category = self.data["config_data"].get("CATEGORY", None)

    def df_compare(self,df_1, df_2, key):
        
        try:
            self.df_1 = df_1
            self.df_2 = df_2
            self.df_1['key'] = self.df_1[key].apply(lambda row: '--'.join(row.values.astype(str)), axis=1)
            self.df_2['key'] = self.df_2[key].apply(lambda row: '--'.join(row.values.astype(str)), axis=1)
            self.df_1.set_index('key', inplace=True)
            self.df_2.set_index('key', inplace=True)
            self.df_1.drop(key, axis=1, inplace=True)
            self.df_2.drop(key, axis=1, inplace=True)
            src_key_values = self.df_1.index.values
            tgt_key_values = self.df_2.index.values
            self.headers = list(set(list(df_1.columns)) - set(key+['key']))
            self.common_keys = list(set(src_key_values) & set(tgt_key_values))
            self.keys_only_in_src = list(set(src_key_values) - set(tgt_key_values))
            self.keys_only_in_tgt = list(set(tgt_key_values) - set(src_key_values))

            self.addExcel()
    
        except Exception:
            traceback.print_exc()
            self.addReasonOfFailure(traceback)
    def truncate(self,f, n):
        return math.floor(f * 10 ** n) / 10 ** n
    def addExcel(self):
        try:
            
            dict1 = { 'REASON OF FAILURE':[]}
            dict3 = {}
            dict2 = { 'Column_Name':[],'Source_Value':[],'Target_Value':[],'REASON OF FAILURE':[]}
            dict4 ={}
            outputFolder = self.data['OUTPUT_FOLDER'] + "\\"
            excelPath = outputFolder + self.configData['NAME'] + '.xlsx'
            excel = ".\\testcases\\" + self.configData['NAME'] + '.xlsx'
            keysCheck =0

            if self.keys_only_in_src:
            
                for i in self.keys_only_in_src:
            
                    li = i.split("--")
                    for i in range(len(li)):
                        key = self.keys[i]
                        self.li1[i].append(li[i])
                        value = self.li1[i]
                        dict3[key] = value
                    dict1.get("REASON OF FAILURE").append("keys only in source")
                    keysCheck +=1
            if self.keys_only_in_tgt:
                for i in self.keys_only_in_tgt:
                    li = i.split("--")
                    for i in range(len(li)):
                        key = self.keys[i]
                        self.li1[i].append(li[i])
                        value = self.li1[i]
                        dict3[key] = value
                    dict1.get("REASON OF FAILURE").append("keys only in target")
                    keysCheck +=1
            valueCheck =0
            if self.common_keys:
                
                for key_val in self.common_keys:
                    for field in self.headers:
                        src_val = self.df_1.loc[key_val,field]
                        tgt_val = self.df_2.loc[key_val,field]
                        if "THRESHOLD" in self.configData:
                            self.reporter.addMisc("Threshold",str(self.configData["THRESHOLD"]))
                            if type(src_val)== numpy.float64 :
                                src_val = self.truncate(src_val,int(self.configData["THRESHOLD"]))
                            if type(tgt_val)== numpy.float64:
                                tgt_val = self.truncate(tgt_val,int(self.configData["THRESHOLD"]))

                        if src_val != tgt_val and type(src_val)==type(tgt_val):
                            valueCheck +=1
                            li = key_val.split('--')
                        
                            for i in range(len(li)):
                                key = self.keys[i]
                                self.li2[i].append(li[i])
                                value = self.li2[i]
                                dict4[key] = value
                            dict2.get('Column_Name').append(field)
                            dict2.get('Source_Value').append(src_val)
                            dict2.get('Target_Value').append(tgt_val)
                            dict2.get('REASON OF FAILURE').append("Difference In Value")
                    
                        elif type(src_val)!= type(tgt_val):

                            valueCheck +=1
                            li = key_val.split('--')
                            for i in range(len(li)):
                                key = self.keys[i]
                                self.li2[i].append(li[i])
                                value = self.li2[i]
                                dict4[key] = value
                            dict2.get('Column_Name').append(field)
                            dict2.get('Source_Value').append(src_val)
                            dict2.get('Target_Value').append(tgt_val)
                            dict2.get('REASON OF FAILURE').append("Difference In Datatype")
            dict3.update(dict1)
            dict4.update(dict2)
            df1_res = pd.DataFrame(dict3)
            df2_res = pd.DataFrame(dict4)
            if (keysCheck+valueCheck) == 0:
                self.reporter.addRow("Data Validation Report","No MisMatch Value Found", status= status.PASS )
                self.logger.info("----No MisMatch Value Found----")
            else:
                self.logger.info("----Adding Data to Excel----")
                with pd.ExcelWriter(excelPath) as writer1:
                    if keysCheck == 0:
                        pass
                    else:
                        df1_res.to_excel(writer1, sheet_name = 'key_difference', index = False)
                    if valueCheck ==0:
                        pass
                    else:
                        df2_res.to_excel(writer1, sheet_name = 'value_difference', index = False)
                self.reporter.addRow("Data Validation Report","DVM Result File: "+'<a href='+excel+'>Result File</a>', status= status.FAIL )
            self.reporter.addMisc("common Keys", str(len(self.common_keys)))
            self.reporter.addMisc("Keys Only in Source",str(len(self.keys_only_in_src)))
            self.reporter.addMisc("Keys Only In Target", str(len(self.keys_only_in_tgt)))

        except Exception as e :
            self.logger.error(str(e))
            self.reporter.addRow("Data Validation Report","Exception Occurred", status.FAIL)
            self.addReasonOfFailure(traceback)

    def addReasonOfFailure(self,rof):
        exceptiondata = rof.format_exc().splitlines()
        exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
        self.reporter.addMisc("reason of failure",exceptionarray[0])
