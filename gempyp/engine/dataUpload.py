import traceback
import requests
import logging
from gempyp.config import DefaultSettings
import logging
import sys


def _getHeaders(bridge_token, user_name):
    """
    for getting the bridgeToken in _sendData method
    """
    return {"Content-Type": "application/json", "bridgeToken": bridge_token, "username": user_name}


def sendSuiteData(payload, bridge_token, user_name, mode="POST"):
    """
    for checking the sendSuiteData api response
    """

    response = _sendData(payload, DefaultSettings.urls["suiteExec"], bridge_token, user_name, mode)
    if response and response.status_code == 201:
        logging.info("data uploaded successfully")

def sendTestcaseData(payload, bridge_token, user_name):
    """
    for checking the sendTestCaseData api response
    """
    try:
        response = _sendData(payload, DefaultSettings.urls["testcases"], bridge_token, user_name, method="POST")
        if response and response.status_code == 201:
            logging.info("data uploaded successfully")

        if response and response.status_code == 201:
            logging.info("data uploaded successfully")

    except Exception as e:
        logging.error(traceback.format_exc())


def _sendData(payload, url, bridge_token, user_name, method="POST"):
    """
    calling the api to upload the data into database
    takes data we need to send(payload),bridgeToken,userName and method as argument
    """
    
    if DefaultSettings.count > 3:
        logging.warning("Incorrect bridgetoken/username or APIs are down. Skipping Data upload.")
        return None
    
    response = requests.request(
        method=method,
        url=url,
        data=payload,
        headers=_getHeaders(bridge_token, user_name),
    )
    if response.status_code != 200 and response.status_code != 201:
        DefaultSettings.count += 1
        logging.info("Data not uploaded...........")
    logging.info(f"status: {response.status_code}")
    return response
