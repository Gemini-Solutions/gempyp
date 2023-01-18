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
from gempyp.libs.common import download_common_file
from gempyp.engine.runner import getError
from gempyp.libs import common

class DvRunner(Base):

    def __init__(self, data):
        
        self.data = data
        self.configData: Dict = self.data.get("config_data")
        self.logger = data["config_data"]["LOGGER"] if "LOGGER" in data["config_data"].keys() else logging
        self.logger.info("---------------------Inside DV FRAMEWORK------------------------")
        self.logger.info(f"-------Executing testcase - \"{self.data['config_data']['NAME']}\"---------")
        if data.get("default_urls", None):
            DefaultSettings.urls.update(data.get("default_urls"))   # only for optimized mode, urls not shared between processes
        # # set vars
        self.setVars()
        # # setting self.reporter object
        self.logger.info("--------------------Report object created ------------------------")
        self.reporter = Base(project_name=self.project, testcase_name=self.tcname)

    def dvEngine(self):
        try:
            try:

                self.validate()
            except Exception as e:
                self.reporter.addMisc("REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))
                self.reporter.addRow("Executing Test steps", f'Something went wrong while executing the testcase- {str(e)}', status.ERR)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.reporter.addRow("Executing Test steps", f'Something went wrong while executing the testcase- {str(e)}', status.ERR)
            common.errorHandler(self.logger, e, "Error occured while running the testcase")
            error_dict = getError(e, self.data["config_data"])
            error_dict["json_data"] = self.reporter.serialize()
            return None, error_dict

        
        sourceCred = None
        targetCred = None
        try:
            column = []
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
                self.reporter.addMisc("REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))
                output = writeToReport(self)
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
                    path = self.configData['SOURCE_CSV']
                    sourceCsvPath = readPath(path)
                    file_obj = download_common_file(sourceCsvPath,self.data.get("SUITE_VARS",None))
                    sourceDelimiter = self.configData.get('SOURCE_DELIMITER',',')
                    self.source_df, self.source_columns = self.csvFileReader(file_obj, sourceDelimiter, "source")
                except Exception as e:
                    self.logger.error(str(e))
                    traceback.print_exc()
                    self.reporter.addRow("Parsing Source File Path","Exception Occurred",status.FAIL)
                    self.reporter.addMisc("REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))
                    output = writeToReport(self)
                    return output, None
            else:
                """Connecting to sourceDB"""
                self.source_df, self.source_columns = self.connectDB(sourceCred, "SOURCE")
            if 'TARGET_CSV' in self.configData:
                try:
                    self.logger.info("Getting Target_CSV File Path")
                    path = self.configData['TARGET_CSV']
                    targetCsvPath = readPath(path)
                    file_obj = download_common_file(targetCsvPath,self.data.get("SUITE_VARS",None))
                    targetDelimiter = self.configData.get('TARGET_DELIMITER',',')
                    self.target_df, self.target_columns = self.csvFileReader(file_obj, targetDelimiter, "Target")
                    # self.target_columns = self.target_df.columns.values.tolist()
                except Exception as e:
                    self.logger.error(str(e))
                    traceback.print_exc()
                    self.reporter.addRow("Parsing Target File Path","Exception Occurred",status.FAIL)
                    self.reporter.addMisc("REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))
                    output = writeToReport(self)
                    return output, None
            else:
                """Connecting to TargetDB"""
                if targetCred==None:
                    self.reporter.addRow("Getting Target Connection Details","Not Found",status.FAIL)
                else:
                    self.target_df, self.target_columns = self.connectDB(targetCred, "TARGET")
            if "BEFORE_FILE" in self.configData:
                self.beforeMethod()
                self.li1 = []
                self.li2 = []
                for i in self.keys:
                    column.append(i)
                    self.li1.append([])
                    self.li2.append([])
                self.matchKeys(self.source_columns,"SOURCE")
                self.matchKeys(self.target_columns,"TARGET")
            try:
                if self.source_columns==self.target_columns:
                    pass
                else:
                    raise Exception
            except Exception:
                self.reporter.addRow("Same Columns in Table","Not Found",status.FAIL)
                self.logger.info("--------Same Column not Present in Both Table--------")
                self.reporter.addMisc("REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))
                output = writeToReport(self)
                return output, None
            
            self.df_compare(self.source_df, self.target_df, self.keys)
            self.reporter.finalizeReport()
            output = writeToReport(self)
            return output, None
        except Exception as e:
            self.logger.error(str(e))
            traceback.print_exc()
            self.reporter.addMisc("REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))
            output = writeToReport(self)
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
        except Exception as e:
            raise Exception(f"Could not read file, {e}")

    def validate(self):
        if "KEYS" in self.configData:
            if 'SOURCE_CONN' in self.configData or 'SOURCE_DB' in self.configData or 'TARGET_CONN' in self.configData or 'TARGET_DB' in self.configData:
                if 'DATABASE' not in self.configData:
                    raise Exception("Tags for Source connection not Present in Config, Please review config.xml")
            elif 'SOURCE_CSV' in self.configData:
                pass
            else:
                raise Exception("Tags for Source connection not Present in Config, Please review config.xml")
        else:
            raise Exception("Keys not Present in Config, Please recheck")

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
            raise Exception(e)
                
        try:
            self.logger.info(f"----Executing the {db}SQL----")
            sql = f"{db}_SQL"
            myCursor.execute(self.configData[sql])
            self.reporter.addRow(f"Executing {db} SQL",f"{self.configData[sql]}<br>{db} SQL executed Successfull",status.PASS)
            columns = [i[0] for i in myCursor.description]
        except Exception as e:
            self.logger.error(str(e))
            self.reporter.addRow(f"Executing {db} SQL","Exception Occurred",status.FAIL)
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
                raise(f"Keys are not Present in {db}")   
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
            self.key_dict = {}
            value_dict = self.addCommonExcel(self.common_keys)
            """calling src and tgt for getting different keys"""
            srcDict = self.addExcel(self.keys_only_in_src, "Source")
            tgtDict = self.addExcel(self.keys_only_in_tgt, "Target")
            self.key_check = len(self.key_dict["REASON OF FAILURE"])
            self.value_check = len(value_dict["REASON OF FAILURE"])
            self.writeExcel(value_dict,self.key_dict)
        except Exception as e:
            traceback.print_exc()
            self.reporter.addMisc("REASON OF FAILURE", common.get_reason_of_failure(traceback.format_exc(), e))


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
                        self.key_dict[key] = value
                    self.dict1.get("REASON OF FAILURE").append(f"keys only in {db}")
            self.key_dict.update(self.dict1)
            return self.key_dict


    def addCommonExcel(self,commonList:list):  

            self.logger.info("In addCommonExcel Function")
            dummy_dict = { 'Column_Name':[],'Source_Value':[],'Target_Value':[],'REASON OF FAILURE':[]}
            comm_dict ={}

            if commonList:
                for key_val in commonList:
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

            logging.info("----------in add excel---------")
            self.logger.info("In Add Excel Function")
            outputFolder = self.data['OUTPUT_FOLDER']
            unique_id = uuid.uuid4()
            excelPath = os.path.join(outputFolder,self.configData['NAME']+str(unique_id)+'.xlsx')
            excel = os.path.join(".","testcases",self.configData['NAME']+str(unique_id)+'.xlsx')
            self.value_df = pd.DataFrame(valDict)
            self.keys_df = pd.DataFrame(keyDict)
            if "AFTER_FILE" in self.configData:
                self.afterMethod()
            if (self.key_check + self.value_check) == 0:
                self.reporter.addRow("Data Validation Report","No MisMatch Value Found", status= status.PASS )
                self.logger.info("----No MisMatch Value Found----")
            else:
                self.logger.info("----Adding Data to Excel----")
                with pd.ExcelWriter(excelPath) as writer1:
                    if self.key_check == 0:
                        pass
                    else:
                        self.keys_df.to_excel(writer1, sheet_name = 'key_difference', index = False)
                    if self.value_check == 0:
                        pass
                    else:
                        self.value_df.to_excel(writer1, sheet_name = 'value_difference', index = False)
                s3_url = None
                try:
                    s3_url = create_s3_link(url=upload_to_s3(DefaultSettings.urls["data"]["bucket-file-upload-api"], bridge_token = self.data["SUITE_VARS"]["bridge_token"], tag="public", username=self.data["SUITE_VARS"]["username"], file=excelPath)[0]["Url"])
                except Exception as e:
                    logging.warn(e)
                if not s3_url:
                    self.reporter.addRow("Data Validation Report",f"""
                    Matched Keys: {len(self.common_keys)}<br>
                    Keys only in Source: {len(self.keys_only_in_src)}<br>
                    Keys only in Target: {len(self.keys_only_in_tgt)}<br>
                    Mismatched Cells: {self.value_check}<br>
                    DV Result File: <a href={excel}>Result File</a>
                    """, status= status.FAIL )
                else:
                    self.reporter.addRow("Data Validation Report",f"""
                    Matched Keys: {len(self.common_keys)}<br>
                    Keys only in Source: {len(self.keys_only_in_src)}<br>
                    Keys only in Target: {len(self.keys_only_in_tgt)}<br>
                    Mismatched Cells: {self.value_check}<br>
                    DV Result File: <a href={s3_url}>Result File</a>""", status= status.FAIL )
                
                self.reporter.addMisc("REASON OF FAILURE",str(f"Mismatched Keys: {self.key_check},Mismatched Cells: {self.value_check}"))
            self.reporter.addMisc("common Keys", str(len(self.common_keys)))
            self.reporter.addMisc("Keys Only in Source",str(len(self.keys_only_in_src)))
            self.reporter.addMisc("Keys Only In Target", str(len(self.keys_only_in_tgt)))
            self.reporter.addMisc("Mismatched Cells", str(self.value_check))


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
            self.logger.info("BEFORE FILE NOT FOUND___________________________")
            self.reporter.addRow("Searching for Before_File steps", "No Before File steps found", status.INFO)

            return
        self.reporter.addRow("Searching for Before_File steps", "Searching for Before File", status.INFO)
        
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
            file_path = download_common_file(file_name,self.data.get("SUITE_VARS",None))
            file_obj= moduleImports(file_path)
            self.logger.info("Running before method")
            obj_ = file_obj
            before_obj = DvObj(
                pg=self.reporter,
                project=self.project,
                source_df=self.source_df,
                target_df=self.target_df,
                source_columns=self.source_columns,
                target_columns=self.target_columns,
                keys=self.keys,
                env=self.env,
            )
            if class_name != "":
                obj_ = getattr(file_obj, class_name)()
            fin_obj = getattr(obj_, method_name)(before_obj)
            self.extractBeforeObj(fin_obj)
            
        except Exception as e:
            self.logger.info(traceback.format_exc())
            self.reporter.addRow("Executing Before method", f"Some error occurred while searching for before method- {str(e)}", status.ERR)
    
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
            self.reporter.addRow("Searching for After_File Steps", "No File Path Found", status.INFO)
            return

        self.reporter.addRow("Searching for After_File", "Searching for File", status.INFO)
        
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
            file_path = download_common_file(file_name, self.data.get("SUITE_VARS", None))
            file_obj= moduleImports(file_path)
            self.logger.info("Running After method")
            obj_ = file_obj
            after_obj = DvObj(
                pg=self.reporter,
                project=self.project,
                value_df = self.value_df,
                keys_df = self.keys_df,
                env=self.env,
            )
            if class_name != "":
                obj_ = getattr(file_obj, class_name)()
            fin_obj = getattr(obj_, method_name)(after_obj)
            self.extractAfterObj(fin_obj)
        except Exception as e:
            self.reporter.addRow("Executing After method", f"Some error occurred while searching for after method- {str(e)}", status.ERR)

    
    def extractBeforeObj(self, obj):
        """To ofload the data from pyprest obj helper, assign the values back to self object"""

        self.reporter = obj.pg
        self.project = obj.project
        self.source_columns = obj.source_columns
        self.target_columns = obj.target_columns
        self.source_df = obj.source_df
        self.target_df = obj.target_df
        self.keys = obj.keys
        self.env = obj.env
    
    def extractAfterObj(self,obj):

        self.reporter = obj.pg
        self.project = obj.project
        self.value_df = obj.value_df
        self.keys_df = obj.keys_df
        self.env = obj.env


