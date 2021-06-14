import sqlite3
import os
import sys
import traceback
import time

class Database():

    DB_LOCATION = 'mydatabase.db'
    def __init__(self) -> None:
        pass
        
    def connect(self):
        try:
            self.connection = sqlite3.connect(Database.DB_LOCATION)
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
    
    def commit(self):
        try:
            self.connection.commit()
            print("Committed")
        except Exception:
            print("Exception occurred in commit {}".format(traceback.format_exc()))
        
    def close(self):
        try:
            self.cursor.close()
            self.connection.close()
            print("Connection Closed")
        except Exception:
            print("Exception occurred in close {}".format(traceback.format_exc()))
            
if __name__ == "__main__":
    pass
