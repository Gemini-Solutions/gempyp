
import os
from configparser import ConfigParser
from posixpath import split
from sqlite3 import connect
from typing import Dict
import pandas as pd
from pyparsing import originalTextFor
import json
import mysql.connector
from gempyp.engine.baseTemplate import testcaseReporter as Base
from gempyp.libs.enums.status import status
from gempyp.dvm.dvmReporting import writeToReport
import sys
from telnetlib import STATUS
import traceback
from numpy import sort
import pandas as pd

class DvmRunner(Base):

    def __init__(self, data):
        self.data = data
        self.configData: Dict = self.data.get("configData")
        # # set vars
        self.setVars()
        # # setting reporter object
        self.reporter = Base(projectName=self.project, testcaseName=self.tcname)
        
    def dvmEngine(self):
        
        try:
            configPath= self.configData["DB_CONFIG_PATH"]
            configur = ConfigParser()
            configur.read(configPath)
            userCred ={"dbuser":configur.get('sourcedb','databaseName'),"sourceName":configur.get('sourcedb','userName'),"password":configur.get('sourcedb','password')}
            targetCred ={"dbuser":configur.get('targetdb','databaseName'),"userName":configur.get('targetdb','userName'),"password":configur.get('targetdb','password')} 
            """code required for database connection"""

            # myDB = mysql.connector.connect(host='localhost',user = 'newuser2', password = ' ', database = 'sourcedb')
            # myCursor = myDB.cursor()
            # myCursor.execute("show database")
            # Create connection object

            # connection = connect(userCred['dbuser'], userCred['userName'], userCred['password'])
        
            # # Create a cursor object
            # cursor = connection.cursor()
        
            # # Run queries
            # cursor.execute('select * from mytable')
            # results = cursor.fetchall()
        
            # # Free resources
            # cursor.close()
            # connection.close()

            ## Create connection object

            # connection = connect(userCred['dbuser'], userCred['userName'], userCred['password'])
        
            # # Create a cursor object
            # cursor = connection.cursor()
        
            # # Run queries
            # cursor.execute('select * from mytable')
            # results = cursor.fetchall()
        
            # # Free resources
            # cursor.close()
            # connection.close()
            array_1 = [[1,'LeBron',3,'0'],
                                [2,'Kobe',5,'1'],
                                [3,'Michael',6,'2'],
                                [4,'Larr','5','3'],
                                [5,'Magic',5,'4'],
                                [6,'Tim',4,'5'],
                                [7,'test1',9,'6']]
            df_1 = pd.DataFrame(array_1, 
                                columns=['id1','Player','Rings','id2'])
            # Data from friend
            array_2 = [[1,'LeBron',3,'1'],
                                [2,'Kobe',3,'9'],
                                [3,'Michael!',6,'2'],
                                [4,'Larry',5,'3'],
                                [5,'Magicl',5,'4'],
                                [6,'Tim',4,'5'],
                                [10,'test2',0,'6']]
            df_2 = pd.DataFrame(array_2, 
                                columns=['id1','Player','Rings','id2'])
            self.df_compare(df_1, df_2, ['id1', 'id2'])
            self.reporter.finalize_report()
            output = writeToReport(self)
            return output, None
        except Exception:
            traceback.print_exc()


    def setVars(self):
        """
        For setting variables like testcase name, output folder etc.
        """
        self.default_report_path = os.path.join(os.getcwd(), "pyprest_reports")
        self.data["OUTPUT_FOLDER"] = self.data.get("OUTPUT_FOLDER", self.default_report_path)
        if self.data["OUTPUT_FOLDER"].strip(" ") == "":
            self.data["OUTPUT_FOLDER"] = self.default_report_path
        self.project = self.data["PROJECTNAME"]
        self.tcname = self.data["configData"]["NAME"]
        self.env = self.data["ENV"]
        self.category = self.data["configData"].get("CATEGORY", None)

    def df_compare(self,df_1, df_2, key):
        try:
            
            df_1['key'] = df_1[key].apply(lambda row: '--'.join(row.values.astype(str)), axis=1)
            df_2['key'] = df_2[key].apply(lambda row: '--'.join(row.values.astype(str)), axis=1)
            df_1.set_index('key', inplace=True)
            df_2.set_index('key', inplace=True)
            df_1.drop(key, axis=1, inplace=True)
            df_2.drop(key, axis=1, inplace=True)
            src_key_values = df_1.index.values
            tgt_key_values = df_2.index.values
            headers = list(set(list(df_1.columns)) - set(key+['key']))
            common_keys = list(set(src_key_values) & set(tgt_key_values))
            keys_only_in_src = list(set(src_key_values) - set(tgt_key_values))
            keys_only_in_tgt = list(set(tgt_key_values) - set(src_key_values))
            diff_list = []
            self.reporter.addMisc("KEYS","--".join(key))
            if keys_only_in_src:
                for i in keys_only_in_src:
                    self.reporter.addRow(str(i),"Key Only In Source",status=status.FAIL)
            if keys_only_in_tgt:
                for i in keys_only_in_tgt:
                    self.reporter.addRow(str(i),"Key Only In Target",status=status.FAIL)
                    
            if common_keys:
                for key_val in common_keys:
                    for field in headers:
                        src_val = df_1.loc[key_val,field]
                        tgt_val = df_2.loc[key_val,field]
                        if src_val != tgt_val and type(src_val)==type(tgt_val):
                            self.reporter.addRow(str(key_val),"Difference In Value",column = str(field),source_value=str(src_val),target_value=str(tgt_val),status=status.FAIL)
                        elif type(src_val)!= type(tgt_val):
                            self.reporter.addRow(str(key_val),"Difference In Datatype",column = str(field),source_value=str(src_val),target_value=str(tgt_val),status=status.FAIL)
                        else:
                            self.reporter.addRow(str(key_val),"No Mismatch Found",column = str(field),source_value=str(src_val),target_value=str(tgt_val),status=status.PASS)

            # if diff_list:
            #     diff_df = pd.DataFrame(diff_list,
            #                     columns=['key','column','src_value', 'tgt_value', 'ROF'])
            #     diff_df.set_index('key', inplace=True)
            #     self.reporter.addRow("difference_table",diff_df.sort_index(axis=0).to_json(orient="split"),status.PASS)
            #     return {'Keys': key,'Common_keys': sorted(common_keys), 'Keys_only_in_source': sorted(keys_only_in_src),
            #     'Keys_only_in_target': sorted(keys_only_in_tgt),'Difference_df': diff_df.sort_index(axis=0).to_json(orient="split")}

            # else:
            #     return -1
        except Exception:
            traceback.print_exc()