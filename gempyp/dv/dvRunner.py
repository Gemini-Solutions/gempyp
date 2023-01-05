import uuid
from gempyp.libs.gem_s3_common import upload_to_s3, create_s3_link
from gempyp.config import DefaultSettings
import mysql.connector
import os
import uuid
from configparser import ConfigParser
from typing import Dict
import pandas as pd
from gempyp.engine.baseTemplate import TestcaseReporter as Base
from gempyp.libs.enums.status import status
from gempyp.libs.common import readPath
from gempyp.dv.dvReporting import writeToReport
from telnetlib import STATUS
import traceback
import pandas as pd
import logging
import math
import numpy
import pg8000

class DvRunner(Base):

    def __init__(self, data):
        
        self.data = data
        self.configData: Dict = self.data.get("config_data")
        self.logger = data["config_data"]["LOGGER"] if "LOGGER" in data["config_data"].keys() else logging
        self.logger.info("---------------------Inside DV FRAMEWORK------------------------")
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
                if "DATABASE" in self.configData:
                    if self.configData["DATABASE"].lower() == 'custom': 
                        pass
                    else:
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
                    # in custom mode we are sending host name using source cred while in other mode we are sending credentenials using sourceCred
                if 'DATABASE' in self.configData:    
                    if self.configData["DATABASE"].lower() == 'custom': 
                        if 'SOURCE_CONN' in self.configData:
                            sourceCred = self.getHost('SOURCE_CONN')
                        if 'TARGET_CONN' in self.configData:
                            targetCred = self.getHost('TARGET_CONN')

                    else:
                        self.logger.info("----Parsing the Config File----")
                        if 'SOURCE_DB' in self.configData:
                            sourceCred ={"host":configur.get(self.configData["SOURCE_DB"],'host'),"dbName":configur.get(self.configData["SOURCE_DB"],'databaseName'),"userName":configur.get(self.configData["SOURCE_DB"],'userName'),"password":configur.get(self.configData["SOURCE_DB"],'password'),"port":configur.get(self.configData["SOURCE_DB"],'port')}
                        if 'TARGET_DB' in self.configData:
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
            """checking whether data is present in csv form or in db"""
            if 'SOURCE_CSV' in self.configData:
                try:
                    self.logger.info("Getting Source_CSV File Path")
                    sourceCsvPath = self.configData['SOURCE_CSV']
                    sourceDelimiter = self.configData.get('SOURCE_DELIMITER',',')
                    db_1, sourceColumns = self.csvFileReader(sourceCsvPath, sourceDelimiter, "source")
                    # sourceColumns = db_1.columns.values.tolist()
                except Exception as e:
                    self.logger.error(str(e))
                    traceback.print_exc()
                    self.reporter.addRow("Parsing Source File Path","Exception Occurred",status.FAIL)
                    output = writeToReport(self)
                    self.addReasonOfFailure(traceback)
                    return output, None
            else:
                """Connecting to sourceDB"""
                db_1, sourceColumns = self.connectDB(sourceCred, "SOURCE")

            if 'TARGET_CSV' in self.configData:
                try:
                    self.logger.info("Getting Target_CSV File Path")
                    targetCsvPath = self.configData['TARGET_CSV']
                    targetDelimiter = self.configData.get('TARGET_DELIMITER',',')
                    db_2, targetColumns = self.csvFileReader(targetCsvPath, targetDelimiter, "Target")
                    # targetColumns = db_2.columns.values.tolist()
                except Exception as e:
                    self.logger.error(str(e))
                    traceback.print_exc()
                    self.reporter.addRow("Parsing Target File Path","Exception Occurred",status.FAIL)
                    output = writeToReport(self)
                    self.addReasonOfFailure(traceback)
                    return output, None
            else:
                """Connecting to TargetDB"""
                db_2, targetColumns = self.connectDB(targetCred, "TARGET")
    
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
            
            self.df_compare(db_1, db_2, self.keys)
            self.reporter.finalizeReport()
            output = writeToReport(self)
            return output, None
        except Exception as e:
            self.logger.error(str(e))
            traceback.print_exc()
            self.addReasonOfFailure(traceback)
            output = writeToReport(self)
            self.addReasonOfFailure(traceback)
            return output, None

    def csvFileReader(self, path, delimiter, db):
        try:
            self.logger.info(f"Reading data from {db} CSV File")
            df = pd.read_csv(path, delimiter)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            columns = df.columns.values.tolist()
            self.reporter.addRow(f"Parsing {db} File","Parsing File is Successfull",status.PASS)
            self.matchKeys(columns, db)
            return df, columns
        except Exception:
            raise Exception


    def connectDB(self,cred, db):
        try:
            log = f"----Connecting to {db}DB----"
            self.logger.info(log)
            dbType = f"{db}DB"
            db_conn = f"{db}_CONN"
            myDB = self.connectingDB(dbType, db_conn, cred)
            myCursor = myDB.cursor()
        except Exception as e:
            self.logger.error(str(e))
            self.reporter.addRow(f"Connection to {db}DB: "+ str(cred["host"]),"Exception Occurred",status.FAIL)
            self.addReasonOfFailure(traceback)
            raise e
                
        try:
            self.logger.info(f"----Executing the {db}SQL----")
            sql = f"{db}_SQL"
            myCursor.execute(self.configData[sql])
            self.reporter.addRow(f"Executing {db} SQL",f"{db} SQL executed Successfull",status.PASS)
            columns = [i[0] for i in myCursor.description]
        except Exception as e:
            self.logger.error(str(e))
            self.reporter.addRow(f"Executing {db} SQL","Exception Occurred",status.FAIL)
            output = writeToReport(self)
            self.addReasonOfFailure(traceback)
            raise e
        
        self.matchKeys(columns, db)
        results = myCursor.fetchall()
        db_1 = pd.DataFrame(results, 
                                columns=columns)
        myDB.close()
        return db_1, columns

    def getHost(self, conn):
        conn_string = self.configData[conn]
        ind = conn_string.index('host')
        count = 0
        li = []
        for i in range(ind,len(conn_string)):
            if conn_string[i] == "'":
                count +=1
                li.append(i)
                if count == 2:
                    break
        host = conn_string[li[0]+1:li[1]]
        return {'host': host}

    def connectingDB(self,db, conn, cred ):

            if self.configData["DATABASE"].lower() == 'custom':
                db1 = self.configData[conn]
                ind = db1.index("(")
                module = db1[0:ind-8:1]
                __import__(module)
                myDB = eval(db1)
                self.reporter.addRow(f"Connection to {db}: "+ cred['host'],f"Connection to {db} is Successfull",status.PASS)
            elif self.configData["DATABASE"].lower() == 'mysql':
                myDB = mysql.connector.connect(host= cred['host'],user = cred["userName"], password = cred['password'],database= cred['dbName'], port = cred['port'])
                self.reporter.addRow(f"Connection to {db}: "+ str(cred["host"]),f"Connection to {db} is Successfull",status.PASS)
            elif self.configData["DATABASE"].lower() == 'postgresql':
                myDB = pg8000.connect(host= cred['host'],user = cred["userName"], password = cred['password'],database= cred['dbName'], port = cred['port'])
                self.reporter.addRow(f"Connection to {db}: "+ str(cred["host"]),f"Connection to {db} is Successfull",status.PASS)
            return myDB     


    def matchKeys(self, columns, db):

        try:
            self.logger.info(f"Matching Keys in {db} DB")
            key = []
            for i in self.keys:
                if i not in columns:
                    key.append(i)
            if len(key)==0:
                self.reporter.addRow(f"Matching Given Keys in {db}",f"Keys are Present in {db}",status.PASS)
                self.logger.info(f"Given Keys are Present in {db} DB")
            else:
                raise (f"Keys are not Present in {db}")   
        except Exception as e:
            keyString1 = ", ".join(key)
            self.reporter.addRow(f"Matching Given Keys in {db}","Keys: " + keyString1 +f" are not Present in {db}DB",status.FAIL)
            self.logger.info("------Given Keys are not present in DB------")


    def df_compare(self,df_1, df_2, key):
    
        try:
            self.logger.info("In df_compare Function")
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
            
            self.value_check = 0
            self.key_check = 0
            self.dict1 = { 'REASON OF FAILURE':[]}
            self.valueDict = {}
            keyDict = self.addCommonExcel(self.common_keys)
            """calling src and tgt for getting different keys"""
            srcDict = self.addExcel(self.keys_only_in_src, "Source")
            tgtDict = self.addExcel(self.keys_only_in_tgt, "Target")
            self.key_check = len(self.valueDict["REASON OF FAILURE"])
            self.value_check = len(keyDict["REASON OF FAILURE"])
            self.writeExcel(self.valueDict,keyDict)
        except Exception:
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
    

    def truncate(self,f, n):

        return math.floor(f * 10 ** n) / 10 ** n
    
    
    def addExcel(self, _list, db):

            if _list:
                for i in _list:
                    li = i.split("--")
                    for i in range(len(li)):
                        key = self.keys[i]
                        self.li1[i].append(li[i])
                        value = self.li1[i]
                        self.valueDict[key] = value
                    self.dict1.get("REASON OF FAILURE").append(f"keys only in {db}")
            self.valueDict.update(self.dict1)
            return self.valueDict


    def addCommonExcel(self,commonList:list):  

            self.logger.info("In addCommonExcel Function")
            dummy_dict = { 'Column_Name':[],'Source_Value':[],'Target_Value':[],'REASON OF FAILURE':[]}
            comm_dict ={}

            if commonList:
                count = 0
                for key_val in commonList:
                    count +=1
                    for field in self.headers:
                        src_val = self.df_1.loc[key_val,field]
                        tgt_val = self.df_2.loc[key_val,field]
                        if src_val == src_val or tgt_val == tgt_val:
                            if "THRESHOLD" in self.configData:
                                self.reporter.addMisc("Threshold",str(self.configData["THRESHOLD"]))
                                if type(src_val)== numpy.float64 and math.isnan(src_val) == False:
                                    src_val = self.truncate(src_val,int(self.configData["THRESHOLD"]))
                                if type(tgt_val)== numpy.float64 and math.isnan(tgt_val) == False:
                                    tgt_val = self.truncate(tgt_val,int(self.configData["THRESHOLD"]))
                            if src_val != tgt_val and type(src_val)==type(tgt_val):
                            
                                li = key_val.split('--')
                                for i in range(len(li)):
                                    key = self.keys[i]
                                    self.li2[i].append(li[i])
                                    value = self.li2[i]
                                    comm_dict[key] = value
                                dummy_dict.get('Column_Name').append(field)
                                dummy_dict.get('Source_Value').append(src_val)
                                dummy_dict.get('Target_Value').append(tgt_val)
                                dummy_dict.get('REASON OF FAILURE').append("Difference In Value")                       
                            
                            elif type(src_val)!= type(tgt_val):
                                
                                li = key_val.split('--')
                                for i in range(len(li)):
                                    key = self.keys[i]
                                    self.li2[i].append(li[i])
                                    value = self.li2[i]
                                    comm_dict[key] = value
                                dummy_dict.get('Column_Name').append(field)
                                dummy_dict.get('Source_Value').append(src_val)
                                dummy_dict.get('Target_Value').append(tgt_val)
                                dummy_dict.get('REASON OF FAILURE').append("Difference In Datatype")
                         
                comm_dict.update(dummy_dict)
                return comm_dict


    def writeExcel(self,valDict,keyDict):
        
            print("----------in add excel---------")
            self.logger.info("In Add Excel Function")
            outputFolder = self.data['OUTPUT_FOLDER'] + "\\"
            excelPath = outputFolder + self.configData['NAME'] + '.xlsx'
            excel = ".\\testcases\\" + self.configData['NAME'] + '.xlsx'
            df1_res = pd.DataFrame(valDict)
            df2_res = pd.DataFrame(keyDict)
            if (self.key_check + self.value_check) == 0:
                self.reporter.addRow("Data Validation Report","No MisMatch Value Found", status= status.PASS )
                self.logger.info("----No MisMatch Value Found----")
            else:
                self.logger.info("----Adding Data to Excel----")
                with pd.ExcelWriter(excelPath) as writer1:
                    if self.key_check == 0:
                        pass
                    else:
                        df1_res.to_excel(writer1, sheet_name = 'key_difference', index = False)
                    if self.value_check ==0:
                        pass
                    else:
                        df2_res.to_excel(writer1, sheet_name = 'value_difference', index = False)
                s3_url = None
                try:
                    s3_url = create_s3_link(url=upload_to_s3(DefaultSettings.urls["data"]["bucket-file-upload-api"], bridge_token = self.data["SUITE_VARS"]["bridge_token"], tag="public", username=self.data["SUITE_VARS"]["username"], file=excelPath, folder="dv")[0]["Url"])

                except Exception as e:
                    print(e)
                if s3_url == None:
                    self.reporter.addRow("Data Validation Report","DVM Result File: "+'<a href='+excel+'>Result File</a>', status= status.FAIL )
                else:
                    self.reporter.addRow("Data Validation Report","DVM Result File: "+'<a href='+s3_url+'>Result File</a>', status= status.FAIL )
            self.reporter.addMisc("common Keys", str(len(self.common_keys)))
            self.reporter.addMisc("Keys Only in Source",str(len(self.keys_only_in_src)))
            self.reporter.addMisc("Keys Only In Target", str(len(self.keys_only_in_tgt)))


    def addReasonOfFailure(self,rof):

        exceptiondata = rof.format_exc().splitlines()
        exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
        self.reporter.addMisc("reason of failure",exceptionarray[0])

