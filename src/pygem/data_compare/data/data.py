import datetime
import os
import sys
import traceback
import threading
import queue
import data_compare.data.database as database

def get_data_thread(config_data, queue1, db_obj = None):
    try:
        print("Data Thread started")
        query = config_data["query"]
        #base_query = config_data["base_query"]
        if not db_obj:
            #will update the db type getting when we will have more type of database
            #add for sqlite
            #db_type = 'sqlite'
            db_type=config_data['type']
            d_obj = database.Database(db_type, config_data)
            db_obj = d_obj.get_db_obj()
            db_obj.connect()
            print("Connected successfully to db")
        #r_val = db_obj.execute_dm_query(query)
        data, header = db_obj.execute_query(query, header=True)
        print("Query executed")
        if not data:
            print("Error in fetching data for query {}".format(query))
        db_obj.close()
        queue1.put((data, header))
        print("Data thread finished")
    except Exception:
        print("Exception in get_data_thread {}".format(traceback.format_exc()))

    finally:
        try:
            db_obj.close()
        except Exception:
            pass

class Data():

    def __init__(self, config_data) -> None:
        self.config_data = config_data
        pass

    def get_data(self):
        try:
            if(self.config_data["src_type"]=="sqlite"):
                src_config = {
                    "type":self.config_data["src_type"],
                    "location":self.config_data["src_location"],
                    "table":self.config_data["srcTable"],
                    #"base_query": "select * from "+self.config_data["srcTable"],
                    "query":self.config_data["src_query_path"],
                    "schema": self.config_data["srcSchema"]
                }
            else:
                src_config = {
                    "type":self.config_data["src_type"],
                    "table":self.config_data["srcTable"],
                    "database":self.config_data["src_database"],
                    #"base_query": "select * from "+self.config_data["srcTable"],
                    "query":self.config_data["src_query_path"],
                    "schema": self.config_data["srcSchema"],
                    "user": self.config_data["src_user"],
                    "password": self.config_data["src_password"],
                    "port":self.config_data["src_port"],
                    "host":self.config_data["src_host"]
                }
            if(self.config_data["tgt_type"]=="sqlite"):	
                tgt_config = {
                    "type":self.config_data["tgt_type"],
                    "location":self.config_data["tgt_location"],
                    "table":self.config_data["tgtTable"],
                    #"base_query": "select * from "+self.config_data["tgtTable"],
                    "query":self.config_data["tgt_query_path"],
                    "schema": self.config_data["tgtSchema"]
                }
            else:
                tgt_config = {
                    "type":self.config_data["tgt_type"],
                    "table":self.config_data["tgtTable"],
                    "database":self.config_data["tgt_database"],
                    #"base_query": "select * from "+self.config_data["tgtTable"],
                    "query":self.config_data["tgt_query_path"],
                    "schema": self.config_data["tgtSchema"],
                    "user": self.config_data["tgt_user"],
                    "password": self.config_data["tgt_password"],
                    "port":self.config_data["tgt_port"],
                    "host":self.config_data["tgt_host"]
                }
            
            if os.path.isfile(src_config["query"]) :
                with open(src_config["query"]) as fobj:
                    print("srcquery file is {}".format(src_config["query"]))
                    src_config["query"] = " ".join(fobj.readlines())
            if os.path.isfile(tgt_config["query"]) :
                with open(tgt_config["query"]) as fobj:
                    print("tgtquery file is {}".format(tgt_config["query"]))
                    tgt_config["query"] = " ".join(fobj.readlines())
            src_queue = queue.Queue()
            tgt_queue = queue.Queue()
            src_thread = threading.Thread(target= get_data_thread, args=(src_config, src_queue))
            src_thread.start()
            print("Src thread started")
            tgt_thread = threading.Thread(target=get_data_thread,args=(tgt_config,tgt_queue))
            tgt_thread.start()
            print("target thread started")
            src_thread.join()
            tgt_thread.join()
            src_data, src_header, tgt_data, tgt_header = None, None, None, None
            if not src_queue.empty():
                src_data,src_header = src_queue.get()
            if not tgt_queue.empty():
                tgt_data,tgt_header = tgt_queue.get()
            #print('1',src_data) 
            #print('2',src_header)
            #print('3',tgt_data)
            #print('4',tgt_header)
            return (src_data,src_header,tgt_data,tgt_header)
            pass
        except Exception:
            print("Exception in get_data {}".format(traceback.format_exc()))
            return (None, None, None, None)
