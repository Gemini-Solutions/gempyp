import importlib
from gempyp.libs.common import readPath, download_common_file, get_reason_of_failure
from gempyp.libs.enums.status import status
from gempyp.dv.dvDatabases import Databases
import traceback
import pandas as pd
import mysql.connector
import snowflake.connector
import pg8000
import re
import time
import pymongo
import json
import ast


class Dataframe:
    def __init__(self) -> None:
        pass

    def getSourceDataFrame(self, data, logger, reporter, sourceCred):
        """checking whether data is present in csv form or in db"""
        self.configData = data.get("config_data")
        self.reporter = reporter
        self.logger = logger
        if 'SOURCE_CSV' in self.configData:
            try:
                logger.info("Getting Source_CSV File Path")
                path = self.configData['SOURCE_CSV']
                sourceCsvPath = readPath(path)
                file_obj = download_common_file(
                    sourceCsvPath, data.get("SUITE_VARS", None))
                sourceDelimiter = self.configData.get(
                    'SOURCE_DELIMITER', ',')
                source_df, source_columns = self.csvFileReader(
                    file_obj, sourceDelimiter, "source")
                return source_df, source_columns
            except Exception as e:
                reporter.addRow(
                    "Parsing source file path", "Exception occurred", status.ERR)
                reporter.addMisc(
                    "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))
                raise Exception(e)
        else:
            """Connecting to sourceDB"""
            if sourceCred == None:
                # reporter.addMisc(
                    # "REASON OF FAILURE", "Source_DB or Source Connection tag not found")
                reporter.addRow("Getting source connection details",
                                "Recheck source_DB tag and source connection tag", status.ERR)
                raise Exception(
                    "Source_db tag or source connection tag not found")
            else:
                source_df, source_columns = self.dbOperations(
                    sourceCred, "SOURCE")
                return source_df, source_columns

    def getTargetDataframe(self, data, logger, reporter, targetCred):
        self.configData = data.get("config_data")
        self.reporter = reporter
        self.logger = logger
        if 'TARGET_CSV' in self.configData:
            try:
                logger.info("Getting Target_CSV File Path")
                path = self.configData['TARGET_CSV']
                targetCsvPath = readPath(path)
                file_obj = download_common_file(
                    targetCsvPath, data.get("SUITE_VARS", None))
                targetDelimiter = self.configData.get(
                    'TARGET_DELIMITER', ',')
                target_df, target_columns = self.csvFileReader(
                    file_obj, targetDelimiter, "Target")
                return target_df, target_columns
            except Exception as e:
                reporter.addRow(
                    "Parsing target file path", "Exception occurred", status.FAIL)
                # reporter.addMisc(
                #     "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))
                raise Exception(e)
        else:
            """Connecting to TargetDB"""
            if targetCred == None:
                # reporter.addMisc(
                #     "REASON OF FAILURE", "Target_DB or Target Connection tag not found")
                reporter.addRow("Getting target connection details",
                                "Recheck for target_db or target connection tag", status.ERR)
                raise Exception(
                    "Target_db or target connection tag not found")
            else:
                target_df, target_columns = self.dbOperations(
                    targetCred, "TARGET")
                return target_df, target_columns

    def setConnection(self, lib, conn):
        lib = importlib.import_module(lib)
        conn = getattr(lib, conn)

    def csvFileReader(self, path, delimiter, db):
        try:
            path=path[0]
            self.logger.info(f"Reading data from {db} CSV File")
            df = pd.read_csv(path, delimiter)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            columns = df.columns.values.tolist()
            self.reporter.addRow(
                f"Parsing {db} file", "Parsing file is successful", status.PASS)
            return df, columns
        except Exception as e:
            raise Exception(f"Could not read file, {e}")

    def dbOperations(self, cred, db):
        try:
            log = f"----Connecting to {db}DB----"
            self.logger.info(log)
            myDB = self.connectingDB(db, cred)
        except Exception as e:
            print("DB Operations..........................................")
            self.reporter.addRow(
                f"Connection to {db}db: ", "Exception occurred", status.ERR)
            self.logger.error(str(e))
            raise Exception(e)
        
        try:
            db_1, columns = self.executeQuery(db, myDB)
        except Exception as e:
            self.logger.error(str(e))
            self.reporter.addRow(
                f"Executing {db} SQL", "Exception Occurred", status.ERR)
            raise e
        return db_1,columns
    
    def fetch_data_with_retries(self, cred, db):
        retry_limit = 3  # Maximum number of connection retry attempts
        retry_delay = 10  # Delay between retry attempts in seconds
        retries = 0
        while retries < retry_limit:
            try:
                return self.dbOperations(cred, db)
            except Exception as e:
                print(f"Connection failed: {str(e)}")
                print("Retrying...")
                print("fetch_data_with_retries...........................")
                time.sleep(retry_delay)
                retries += 1

        print("Maximum number of retries exceeded. Failed to fetch data.")
        return None, None

    
    def executeQuery(self,db,myDB):
        try:
            self.logger.info(f"----Executing the {db}SQL----")
            # checking whether it is mongodb object by checking mongoclient in starting of the object
            x = re.search("^MongoClient.*", str(myDB))
            if x:
                try:
                    db_name = f'{db}_DB'
                    db_details = ast.literal_eval(self.configData[db_name])
                    sql = f'{db}_SQL'
                    conn = myDB[db_details['database']]
                    list_of_collections = conn.list_collection_names()
                    if db_details['collection'] not in list_of_collections:
                        raise Exception
                    conn = conn[db_details['collection']]
                except Exception:
                    self.reporter.addRow("Finding database and collection","Not found in source_db or target_db",status.ERR)
                    raise Exception("Database and collection not found in source_db or target_db")
                try:
                    query = json.loads(self.configData[sql])
                except Exception:
                    self.reporter.addRow("Fetching query","Not present in json format",status.ERR)
                    raise Exception("Mongo query not present in json format")
                results = list(conn.find(query))
                db_1 = pd.DataFrame(results)
                columns = list(db_1.columns)
            else:
                # try:
                myCursor = myDB.cursor()
                sql = f"{db}_SQL"
                statement_timeout = 0
                myDB.cursor().execute(f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = {statement_timeout}")
                myDB.cursor().execute(f"alter warehouse COMPUTE_WH set statement_timeout_in_seconds = {statement_timeout}")
                myCursor.execute(self.configData[sql])
                self.reporter.addRow(
                    f"Executing {db} sql", f"{self.configData[sql]}<br>{db} sql executed successfull", status.PASS)
                columns = [i[0] for i in myCursor.description]
                results = myCursor.fetchall()
                db_1 = pd.DataFrame(results,columns=columns)
        except Exception as e:
            self.logger.error(str(e))
            # self.reporter.addMisc(
            #         "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))

            self.reporter.addRow(
                f"Executing {db} sql", "Exception occurred", status.ERR)
            raise e
        
        myDB.close()
        return db_1, columns

    def connectingDB(self, dbType, cred):
        
        db = f'{dbType}_DB'
        is_dict = True
        try:
            db_details = ast.literal_eval(self.configData[db])
        except Exception:
            is_dict = False
        if is_dict == True:
            db_type = db_details.get('type')
        else:
            db_type = self.configData[db]
                    
        if db_type.lower() == 'custom':
            conn = f"{dbType}_CONN"
            db = self.configData[conn]
            myDB = eval(db)
            # this is just to check whether connection is established or not
            x = re.search("^MongoClient.*", str(myDB))
            if x:
                myDB.server_info()
            else:
                dbCursor = myDB.cursor()
            self.reporter.addRow(
                f"Connection to {dbType}db:", f"Connection to {dbType}db is successfull", status.PASS)
        else:
            dv = Databases()
            lib, connect = Databases.getConnectionString(
                dv, db_type)
            lib = importlib.import_module(lib)
            connection = getattr(lib, connect)
            myDB = connection(**cred)
            x = re.search("^MongoClient.*", str(myDB))
            if x:
                myDB.server_info()
            connDetails = self.getHostDetails(cred)
            self.reporter.addRow(
                f"Connection to {dbType}db: {connDetails}", f"Connection to {dbType}db is successful", status.PASS)
        return myDB

    def getHostDetails(self, details):

        li = list(details.keys())
        for i in li:
            if re.search("user", i) != None:
                del details[i]
                continue
            if re.search("password", i) != None:
                del details[i]
        return details