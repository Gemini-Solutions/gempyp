import os
import json
import logging
from datetime import datetime
import traceback
from typing import List, Union
import typing
from gempyp.config import DefaultSettings
import importlib
import sys
from gempyp.libs.gem_s3_common import download_from_s3
from gempyp.config.GitLinkXML import fetchFileFromGit


def read_json(file_path):
    try:
        with open(file_path) as fobj:
            res = json.load(fobj)
            print(res)
    except Exception:
        res = None
    return res
def readPath(file_name):
        try:
            conf = file_name.split(os.sep)
            if conf[0] == ".." or conf[0]==".":
                script_path, script_name = importFromPath(file_name)
                for each in sys.path:
                    if isinstance(each,dict) and each is not None:
                        logging.info("--------- Fetching config path - {} ------".format( each['XMLConfigDir']))
                        lib_path = os.path.join(each['XMLConfigDir'], file_name)
                        return lib_path
            else:
                return file_name
        except Exception as e:
            traceback.print_exc()


def findDuration(start_time: datetime, end_time: datetime):
    # finds the duration in the form HH MM SS

    duration = end_time - start_time
    seconds = duration.total_seconds()
    mins = seconds // 60
    seconds = seconds % 60

    if mins > 0:
        return f"{mins} mins and {round(seconds, 3)} seconds"
    return f"{round(seconds, 3)} seconds"


def errorHandler(logging, Error, msg="some Error Occured"):

    logging.error(msg)
    logging.error(f"Error: {Error}")

    if DefaultSettings.DEBUG:
        logging.error(f"TraceBack: {traceback.format_exc()}")


def parseMails(mail: Union[str, typing.TextIO]) -> List:
    try:

        if hasattr(mail, "read"):
            mails = mail.read()

        elif os.path.isfile(mail):
            file = open(mail, "r")
            mails = file.read()
            file.close()

        mails = mail.strip()
        mails = mails.split(",")
        return mails
    except Exception as e:
        logging.error("Error while parsing the mails")
        logging.error(f"Error : {e}")
        logging.error(f"traceback: {traceback.format_exc()}")
        return []


# custom encoder to encode date to epoch
class dateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.timestamp()*1000
        return json.JSONEncoder.default(self, o)

# absolute path path.... moved to file from runner due to circular import issue
# runner -> gempyp -> abstractsimpletestcase -> runner
def importFromPath(file_name):
    logging.info("--------- In import from path ----------")
    path_arr = file_name.split(os.sep)    
    file = path_arr[-1]
    path_arr.remove(file)
    path_cd = os.sep.join(path_arr)
    return path_cd, file
    
def moduleImports(file_name):
    import_flag = 0
    try:
        logging.info("--------Trying importing modules--------")
        dynamicTestcase = importlib.import_module(file_name)       
        return dynamicTestcase
    except Exception as i:
        logging.info("-------Testcase not imported as module, Trying with absolute path-------")
        try:
            script_path, script_name = importFromPath(file_name)
            script_name = script_name.split(".")[0]
            if script_path is not None:
                sys.path.append(script_path)
            try:
                dynamicTestcase = importlib.import_module(script_name) 
            except Exception:
                logging.info("when absolute and module import both failed")
                try:
                    for each in sys.path:
                        if isinstance(each,dict) and each is not None:
                            logging.info("--------- Fetching config path - {} ------".format( each['XMLConfigDir']))
                            lib_path = os.path.join(each['XMLConfigDir'], script_path)
                    sys.path.append(lib_path)
                    dynamicTestcase = importlib.import_module(script_name.split(".")[0])
                    import_flag = 1 
                except Exception:
                    traceback.print_exc()
                if import_flag != 1:
                    traceback.print_exc()
            return dynamicTestcase
        except Exception as e:
            logging.error("----- Error occured file could not be imported using any of the methods.-----")
            traceback.print_exc()
            return e




def download_beforeAfter_file(file_name,headers):
    if(file_name.__contains__('S3')):
        logging.info("File is from S3")
        fileContent=download_from_s3(api=file_name.replace("S3:",""),username=headers.get("username",None),bridge_token=headers.get("bridge_token",None))
        file_name = os.path.join(file_name.split(":")[-1])
        with open(file_name, "w+") as fp:
            fp.seek(0)
            fp.write(fileContent)
            fp.truncate()
    elif(file_name.__contains__('GIT')):
        logging.info("File is from GIT")
        list_url=file_name.split(":")
        if(len(list_url)>=5):
            file_name=fetchFileFromGit(list_url[2],list_url[3],username=list_url[-2],bearer_token=list_url[-1])
        else:
            file_name=fetchFileFromGit(list_url[2],list_url[3])
    file_name= moduleImports(file_name)



    return file_name
            


