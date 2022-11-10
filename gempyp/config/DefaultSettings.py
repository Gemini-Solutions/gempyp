import os
from gempyp.engine import dataUpload
import traceback
import logging

# have to discuss about the default location
DEFAULT_GEMPYP_FOLDER = os.getcwd()
DEBUG = True
THREADS = 8
_VERSION = "1.0.0"

urls = {}
# for getting urls using url tag from config file
def getParams(params):
    
    PARAMS = params
    global urls
    urls = {"data":{
                "jewel-url": "https://jewel.gemecosystem.com",
                "suiteInfo": "https://apis.gemecosystem.com/suiteinfo/",
                "suite-exe-api": "https://apis.gemecosystem.com/suiteexe",
                "test-exe-api": "https://apis.gemecosystem.com/testcase",
            }
        }
   
    try:
        #checking if url is present in file and calling get api
        if "BASE_URL" in PARAMS:
            url = PARAMS["BASE_URL"]
            response = dataUpload._sendData(" ", url, PARAMS["BRIDGE_TOKEN"],PARAMS["USERNAME"] ,"GET")
            if response.status_code == 200:
                urls = response.json()
            else:
                logging.warning("Error Occurs While Getting the BASE_URLs")
    except Exception as e:
            traceback.print_exc()
            logging.warning("Error Occurs While Getting the URLs")
# for sending urls to dataupload file
def getUrls(apiName):
        return urls["data"][apiName]

count = 0
