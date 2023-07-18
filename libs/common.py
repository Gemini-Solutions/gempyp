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
from gempyp.libs.gem_s3_common import download_from_s3, upload_to_s3, create_s3_link
from gempyp.config.GitLinkXML import fetchFileFromGit
from gempyp.config import DefaultSettings
from gempyp.engine import dataUpload
import logging
import requests
from gempyp.engine.dataUpload import _getHeaders
import re


def read_json(file_path):
    try:
        with open(file_path) as fobj:
            res = json.load(fobj)
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
        if(mail is not None):
            if hasattr(mail, "read"):
                mails = mail.read()

            elif os.path.isfile(mail):
                file = open(mail, "r")
                mails = file.read()
                file.close()
            mails = mail.strip()
            emails=[]
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            for mail in mails.split(","):
                if(re.fullmatch(regex, mail)):
                    emails.append(mail)
            return emails
    except Exception as e:
        logging.error("Error while parsing the mails")
        logging.error(f"Error : {e}")
        logging.error(f"traceback: {traceback.format_exc()}")
        return []

def remove_none_from_dict(data):
    try:
        key_list = [key for key in data.keys()]
        for key in key_list:
            if isinstance(data[key], dict):
                remove_none_from_dict(data[key])
            if not data[key]:
                del data[key]
    except Exception as e:
        traceback.print_exc()
        pass
    return data


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
    if not file_name:
        return None
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

def download_common_file(file_name,headers=None):
     try:
        if file_name and (file_name.__contains__('S3:')):
            logging.info("File is from S3")
            response=download_from_s3(api=file_name.replace("S3:",""),username=headers.get("username",None),bridge_token=headers.get("bridge_token",None))
            if(response.status_code==200):
                file_name = os.path.join(file_name.split(":")[-1])
                with open(file_name, "w+") as fp:
                    fp.seek(0)
                    fp.write(response.text)
                    fp.truncate()
            else:
                logging.info(response.status_code)
                logging.info(response.text)
        elif file_name and (file_name.__contains__('GIT')):
            logging.info("File is from GIT")
            list_url=file_name.split(":")
            if(len(list_url)>=5):
                file_name=fetchFileFromGit(list_url[2],list_url[3],username=list_url[-2],bearer_token=list_url[-1])
            else:
                file_name=fetchFileFromGit(list_url[2],list_url[3])
        return file_name
     except Exception as e:
        traceback.print_exc()
        return e
            

def control_text_size(data, **kwargs):

    fin_str = data
    if len(str(data)) > 150:
        url = None
        try:
            url = create_s3_link(url=upload_to_s3(DefaultSettings.urls["data"]["bucket-data-upload-api"], data=data, bridge_token=kwargs.get("bridge_token", None), username=kwargs.get("username", None), tag="public")["Url"])
            if url:
                fin_str = f'<a target=_blank  href={url}>Click here</a>'
        except Exception as e:
            logging.info(e)
    return fin_str


def check_json(data):
    try:
        data = json.loads(str(data))
    except Exception as e:
        logging.WARN(traceback.format_exc())

    return data

def get_reason_of_failure(data, e=None):  
    try:
        exceptiondata = data.splitlines()
        exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
        return exceptionarray[0]
    except:
        return e


def validateZeroTestcases(testcaseLength):
    if not testcaseLength:  # in case of zero testcases, we should not insert suite data 
            logging.warning("NO TESTCASES TO RUN..... PLEASE CHECK RUN FLAGS. ABORTING.................")
            sys.exit()
            


def runBaseUrls(jewel_user,base_url,username,bridgetoken):
    
            #trying rerun of base url api in case of api failure
            if base_url and DefaultSettings.apiSuccess == False:
                logging.info("Trying to call Api for getting urls")
                DefaultSettings.getEnterPoint(base_url ,bridgetoken,username)
            if not base_url:
                DefaultSettings.getEnterPoint(DefaultSettings.default_baseurl ,bridgetoken, username)


def sendMail(s_run_id,mails,bridge_token,username):
    try:
        # payload={"to": mails, "s_run_id": s_run_id}
        mails["s_run_id"]=s_run_id
        response = requests.request(
        method="POST",
        url=DefaultSettings.getUrls("email-api"),
        data=json.dumps(mails),
        headers=_getHeaders(bridge_token, username),
        )
        if response.status_code == 200:
            logging.info("Report successfully sent on mail")
        else:
            logging.info(response.text)
    except Exception as e:
        traceback.print_exc()

        