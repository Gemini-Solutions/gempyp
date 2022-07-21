import traceback
import requests
import logging
from gempyp.config import DefaultSettings
from gempyp.libs import common
import logging


def _getHeaders(bridgeToken, user_name):

    return {"Content-Type": "application/json", "bridgetoken": bridgeToken, "username": user_name}



def sendSuiteData(payload, bridgeToken, user_name, mode="POST"):
    try:
        response = _sendData(payload, DefaultSettings.urls["suiteExec"], bridgeToken, user_name, mode)
        if response.status_code == 201:
            logging.info("data uploaded successfully")

    except Exception as e:
        logging.error(traceback.format_exc())

def sendTestcaseData(payload, bridgeToken, user_name):
    try:
        response = _sendData(payload, DefaultSettings.urls["testcases"], bridgeToken, user_name, method="POST")

        if response.status_code == 201:
            logging.info("data uploaded successfully")

    except Exception as e:
        logging.error(traceback.format_exc())


def _sendData(payload, url, bridgeToken, user_name, method="POST"):

    response = requests.request(
        method=method,
        url=url,
        data=payload,
        headers=_getHeaders(bridgeToken, user_name),
    )
    logging.info(f"status: {response.status_code}")
    response.raise_for_status()

    return response
