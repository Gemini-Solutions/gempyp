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
urls = {"data":{
                "jewel-url": "https://jewel.gemecosystem.com",
                "suiteInfo": "https://apis.gemecosystem.com/suiteinfo/",
                "suite-exe-api": "https://apis.gemecosystem.com/suiteexe",
                "test-exe-api": "https://apis.gemecosystem.com/testcase",
            }
        }
# for getting urls using url tag from config file
def getEnterPoint(url, bridge_token, user_name):

    global urls
   
    try:
            url = checkUrl(url)
            response = dataUpload._sendData(" ", url, bridge_token, user_name,"GET")
            if response.status_code == 200:
                urls = response.json()
                global apiSuccess
                apiSuccess = True
            else:
                logging.warning("Error Occurs While Getting the BASE_URLs")
    except Exception as e:
            traceback.print_exc()
            logging.warning("Error Occurs While Getting the BASE_URLs")
# for sending urls to dataupload file
def getUrls(apiName):
        return urls["data"][apiName]

def checkUrl(url):
    try:
        l = url.index('.com')
        url = url[:l+4:] + "/enter-point"
        return url
    except Exception:
        traceback.print_exc()
        logging.warning("Error Occurs While handling the BASE_URLs")

count = 0
