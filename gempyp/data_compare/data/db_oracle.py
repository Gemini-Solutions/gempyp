import cx_Oracle
import os
import sys
import traceback
import time
import common.common_functions as cf

class Database():
    def __init__(self, config_data) -> None:
        try:
            self.user = config_data.get('user',None)
            self.password = config_data.get('password',None)
            self.database = config_data.get('database',None)
            self.port = config_data.get('port',None)
            self.dsn = config_data.get('dsn',None)
        except Exception as exc:
            print("Exception in __init__ of db_oracle.Database {}".format(str(exc)))
    
    def connect(self,threaded = False):
        try:
            if not self.dsn:
                if self.user and self.password and self.database and self.port:
                    self.dsn = self.user + "/" +cf.decrypt(self.password) +"@" + self.database+":"+self.port
                elif self.database:
                    self.dsn = "/@"+self.database
            if threaded:
                self.con = cx_Oracle.connect(self.dsn,threaded=True)
            else:
                self.con = cx_Oracle.connect(self.dsn)
            print("Connected to db successfully")
            self.cursor = self.con.cursor()
            self.cursor.arraysize = 1000
            print("cursor created successfully")
        except Exception:
            print("Exception occured in connect {}".format(traceback.format_exc()))

    def execute_query(self, query, header = True):
        """
        We will be only executing select from this so we are adding header as param
        """
        try:
            self.cursor.execute(query)
            res = self.cursor.fetchall()
            if header:
                q_header = [x[0] for x in self.cursor.description]
            else:
                q_header = []

        except Exception:
            res = None
            q_header = None
            print("Exception in execute_query {}".format(traceback.format_exc()))
        return res,q_header if header else res

    def execute_dm_query(self, query):
        try:
            r_val = 1
            self.cursor.execute(query)
            self.con.commit()
            r_val = 0
        except Exception:
            self.con.rollback()
            print("Exception occured in execute_dml_query {}".format(traceback.format_exc()))
        return r_val
    
    def close(self):
        try:
            print("CLosing db connection")
            self.con.close()
            print("Db connection closed")
        except Exception:
            pass

if __name__ == "__main__":
    pass
