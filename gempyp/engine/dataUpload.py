import traceback
import requests
import logging
from gempyp.config import DefaultSettings
import logging
import sys
import re
import json

not_uploaded = []
suite_data = []
flag = False
s_flag = False
suite_not_uploaded = False
def _getHeaders(bridge_token, user_name):
    """
    for getting the bridgeToken in _sendData method
    """
    return {"Content-Type": "application/json", "bridgeToken": bridge_token, "username": user_name}

def checkingData(run_id, bridge_token, user_name):
    url = DefaultSettings.urls["suiteExec"] + "?s_run_id=" + run_id
    print(url)
    response = _sendData("", url , bridge_token, user_name, "GET")
    if response.status_code == 200:
        return response._content
    else:
        return "failed"

def sendSuiteData(payload, bridge_token, user_name, mode="POST"):
    """
    for checking the sendSuiteData api response
    """
    ### for removing none value in payload
    try:
        payload = noneRemover(payload)
        response = _sendData(payload, DefaultSettings.urls["suiteExec"], bridge_token, user_name, mode)
        ### Applying regex to the response
        x = re.search("already present",response.text,re.IGNORECASE)

        if response and response.status_code == 201:
            logging.info("data uploaded successfully")
            global suite_not_uploaded
            suite_not_uploaded = True
            if payload in suite_data:
                suite_data.remove(payload)
        else:
            if payload not in suite_data:
                suite_data.append(payload)
                if x != None:
                    global s_flag
                    s_flag = True
    except Exception as e:
        logging.error(traceback.format_exc())

def sendTestcaseData(payload, bridge_token, user_name):
    """
    for checking the sendTestCaseData api response
    """
    try:
        # if payload["tc_run_id"]=="1234":
        response = _sendData(payload, DefaultSettings.urls["testcases"], bridge_token, user_name, method="POST")
        ### Applying regex to the response
        x = re.search("already present",response.text,re.IGNORECASE)
        if response and response.status_code == 201:
            logging.info("data uploaded successfully")
            if payload in not_uploaded:
                not_uploaded.remove(payload)

    ### code for rerun of unuploaded testcases
        else:
            if payload not in not_uploaded:
                not_uploaded.append(payload)
                if x != None:
                    global flag
                    flag = True

    except Exception as e:
        logging.error(traceback.format_exc())


def _sendData(payload, url, bridge_token, user_name, method="POST"):
    """
    calling the api to upload the data into database
    takes data we need to send(payload),bridgeToken,userName and method as argument
    """
    
    # Not needed anymore as we will be reuploading the data to db.
    # if DefaultSettings.count > 3:         
    #     logging.warning("Incorrect bridgetoken/username or APIs are down. Skipping Data upload.")
    #     return None

    response = requests.request(
        method=method,
        url=url,
        data=payload,
        headers=_getHeaders(bridge_token, user_name),
    )
    if response.status_code != 200 and response.status_code != 201:
        # DefaultSettings.count += 1
        logging.info("Data not uploaded...........")
    logging.info(f"status: {response.status_code}")
    return response

def noneRemover(payload):
    
    data = json.loads(payload)
    for key,value in dict(data).items():
        if value == "-":
            del data[key]
    return json.dumps(data)