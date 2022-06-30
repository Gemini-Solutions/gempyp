import sqlite3
import os
import sys
import traceback
import time

class Database():

    def __init__(self, config_data) -> None:
        self.location = config_data.get("location",None)
        
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.location)
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
    
