import importlib
from gempyp.libs.common import readPath, download_common_file, get_reason_of_failure
from gempyp.libs.enums.status import status
from gempyp.dv.dvDatabases import Databases
import traceback
import pandas as pd
import mysql.connector
# import snowflake.connector
import pg8000
import re


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
                    "Parsing Source File Path", "Exception Occurred", status.ERR)
                reporter.addMisc(
                    "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))
                raise Exception(e)
        else:
            """Connecting to sourceDB"""
            if sourceCred == None:
                # reporter.addMisc(
                    # "REASON OF FAILURE", "Source_DB or Source Connection tag not found")
                reporter.addRow("Getting Source Connection Details",
                                "Recheck Source_DB Tag and Source Connection Tag", status.ERR)
                raise Exception(
                    "Source_DB Tag or Source Connection Tag NOT FOUND")
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
                    "Parsing Target File Path", "Exception Occurred", status.FAIL)
                # reporter.addMisc(
                #     "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))
                raise Exception(e)
        else:
            """Connecting to TargetDB"""
            if targetCred == None:
                # reporter.addMisc(
                #     "REASON OF FAILURE", "Target_DB or Target Connection tag not found")
                reporter.addRow("Getting Target Connection Details",
                                "Recheck for Target_DB or Target Connection Tag", status.ERR)
                raise Exception(
                    "Target_DB or Target Connection Tag Not Found")
            else:
                target_df, target_columns = self.dbOperations(
                    targetCred, "TARGET")
                return target_df, target_columns

    def setConnection(self, lib, conn):
        lib = importlib.import_module(lib)
        conn = getattr(lib, conn)

    def csvFileReader(self, path, delimiter, db):
        try:
            self.logger.info(f"Reading data from {db} CSV File")
            df = pd.read_csv(path, delimiter)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            columns = df.columns.values.tolist()
            self.reporter.addRow(
                f"Parsing {db} File", "Parsing File is Successfull", status.PASS)
            return df, columns
        except Exception as e:
            raise Exception(f"Could not read file, {e}")

    def dbOperations(self, cred, db):
        try:
            log = f"----Connecting to {db}DB----"
            self.logger.info(log)
            myDB = self.connectingDB(db, cred)
            myCursor = myDB.cursor()
        except Exception as e:
            self.reporter.addRow(
                f"Connection to {db}DB: ", "Exception Occurred", status.ERR)
            self.logger.error(str(e))
            # self.reporter.addMisc(
            #         "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))

            raise Exception(e)

        try:
            self.logger.info(f"----Executing the {db}SQL----")
            sql = f"{db}_SQL"
            myCursor.execute(self.configData[sql])
            self.reporter.addRow(
                f"Executing {db} SQL", f"{self.configData[sql]}{db} SQL executed Successfull", status.PASS)
            columns = [i[0] for i in myCursor.description]
        except Exception as e:
            self.logger.error(str(e))
            # self.reporter.addMisc(
            #         "REASON OF FAILURE", get_reason_of_failure(traceback.format_exc(), e))

            self.reporter.addRow(
                f"Executing {db} SQL", "Exception Occurred", status.ERR)
            raise e

        results = myCursor.fetchall()
        db_1 = pd.DataFrame(results,
                            columns=columns)
        myDB.close()
        return db_1, columns

    def connectingDB(self, dbType, cred):
        
        db = f'{dbType}_DB'
        if self.configData[db].lower() == 'custom':
            conn = f"{dbType}_CONN"
            db = self.configData[conn]
            myDB = eval(db)
            # this is just to check whether connection is established or not
            dbCursor = myDB.cursor()
            self.reporter.addRow(
                f"Connection to {dbType}DB:", f"Connection to {dbType}DB is Successfull", status.PASS)
        else:
            dv = Databases()
            lib, connect = Databases.getConnectionString(
                dv, self.configData[db])
            lib = importlib.import_module(lib)
            connection = getattr(lib, connect)
            myDB = connection(**cred)
            connDetails = self.getHostDetails(cred)
            self.reporter.addRow(
                f"Connection to {dbType}DB: {connDetails}", f"Connection to {dbType}DB is Successfull", status.PASS)
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
