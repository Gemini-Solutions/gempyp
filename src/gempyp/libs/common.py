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


def read_json(file_path):
    try:
        # print(file_path)
        with open(file_path) as fobj:
            res = json.load(fobj)
    except Exception:
        res = None
    return res


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
    print("--------- In import from path ----------")
    if os.name == 'nt':
        path_arr = (file_name.split("\\"))
        print(path_arr)
    else:
        path_arr = filename.split("/")
    file = path_arr[-1]
    print("------------------", file)
    path_arr.remove(file)
    path_cd = '/'.join(path_arr)
    print("-------------", path_cd, "---------", file_name)
    return path_cd, file

def moduleImports(file_name):
    print("---- file name", file_name)
    try:
        dynamicTestcase = importlib.import_module(file_name)
        return dynamicTestcase
    except Exception as i:
        print("Testcase not imported as module, Trying with absolute path")
        try:
            script_path, script_name = importFromPath(file_name)
            script_name = script_name[0:-3]
            sys.path.append(script_path)
            dynamicTestcase = importlib.import_module(script_name)
            return dynamicTestcase
        except Exception as e:
            print("Error occured while running from absolute path")
            return e
