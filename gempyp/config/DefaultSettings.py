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
                "jewel-url": "https://jewel-beta.gemecosystem.com",
                "suiteInfo": "https://apis-beta.gemecosystem.com/suiteinfo/",
                "suite-exe-api": "https://apis-beta.gemecosystem.com/suiteexe",
                "test-exe-api": "https://apis-beta.gemecosystem.com/testcase",
                "last-five": "https://apis-beta.gemecosystem.com/suiteexe/lastFive",
                "comment-api": "https://apis-beta.gemecosystem.com/jira/comment",
                "jira-api": "https://apis-beta.gemecosystem.com/jira/create",
            }
        }
# for getting urls using url tag from config file
def getEnterPoint(url, bridge_token, user_name):
    global urls
    try:
        url = checkUrl(url)
        response = dataUpload._sendData(" ", url, bridge_token, user_name,"GET")
        if response.status_code == 200:
            url_enter_point = response.json()
            urls["data"].update(url_enter_point["data"])
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
        url = url[:l+4:] + "/enter-point"
        return url
    except Exception:
        traceback.print_exc()
        logging.warning("Error Occurs While handling the BASE_URLs")

count = 0
