import os
from gempyp.engine import dataUpload
import traceback
import logging

# have to discuss about the default location
DEFAULT_GEMPYP_FOLDER = os.getcwd()
DEBUG = True
THREADS = 8
_VERSION = "1.0.0"
apiSuccess = False
project_id = "Test_id"
default_baseurl="https://apis.gemecosystem.com"
urls = {"data":{} }
# for getting urls using url tag from config file
def getEnterPoint(url, bridge_token, user_name):
    global urls
    try:
        url = checkUrl(url)
        response = dataUpload._sendData(" ", url, bridge_token, user_name,"GET")
        if response.status_code == 200:
            url_enter_point = response.json()
            urls["data"]=url_enter_point["data"]
            global apiSuccess
            apiSuccess = True
        else:
            logging.warning("Error Occurs While Getting the BASE_URLs")
    except Exception as e:
            traceback.print_exc()
            logging.warning("Error Occurs While Getting the BASE_URLs")

# for sending urls to dataupload file
def getUrls(apiName):
    return urls["data"].get(apiName, None)

def checkUrl(url):
    try:
        l = url.index('.com')
        # url = url[:l+4:] + "/enter-point"
        if(url.__contains__("/enter-point")):
            return url
        else:
            return url.strip("/")+"/enter-point"
    except Exception:
        traceback.print_exc()
        logging.warning("Error Occurs While handling the BASE_URLs")

count = 0
