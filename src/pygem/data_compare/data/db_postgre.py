import psycopg2
import os
import sys
import traceback
import time
import common.common_functions as cf

class Database():

    
    def __init__(self, config_data) -> None:
        self.user = config_data.get("user",None)
        self.host = config_data.get("host", None)
        self.port = config_data.get("port", None)
        if isinstance(self.port,str):
            self.port = int(self.port)
        self.password = config_data.get("password", None)
        self.database = config_data.get("database", None)
        
    def connect(self):
        try:
            self.connection = psycopg2.connect(host = self.host, user = self.user, password = cf.decrypt(self.password), port = self.port,database = self.database)
            print("Connected Successfully")
            self.cursor = self.connection.cursor()
            print("Cursor Created")
        except Exception:
            print("Exception occurred in connect {}".format(traceback.format_exc()))
           
    def execute_query(self, query, header = False):
        try:
            self.cursor.execute(query)
            res = self.cursor.fetchall()
            if(header):
                q_header = [x[0] for x in self.cursor.description]
            else:
                q_header = []
        except Exception:
            res = None
            q_header = None
            print("Exception occurred in execute_query {}".format(traceback.format_exc()))
        return res, q_header if header else res
        
    def execute_dm_query(self, query):
        try:
            r_val = 1
            self.cursor.execute(query)
            self.connection.commit()
            r_val = 0
        except Exception:
            self.connection.rollback()
            print("Exception occured in execute_dml_query {}".format(traceback.format_exc()))
        return r_val
    
    def commit(self):
        try:
            self.connection.commit()
            print("Committed")
        except Exception:
            print("Exception occurred in commit {}".format(traceback.format_exc()))
        
    def close(self):
        try:
            #self.cursor.close()
            self.connection.close()
            print("Connection Closed")
        except Exception:
            print("Exception occurred in close {}".format(traceback.format_exc()))
            
if __name__ == "__main__":
    pass
