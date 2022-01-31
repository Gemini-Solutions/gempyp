import requests
import logging
from pygem.config import DefaultSettings
from pygem.libs import common


def _getHeaders():

    return {"Content-Type": "application/json"}


def sendSuiteData(payload, mode="POST"):

    try:
        response = _sendData(payload, DefaultSettings.urls["suiteExec"], mode)
        if response.status_code == 201:
            logging.info("data uploaded successfully")

    except Exception as e:
        common.errorHandler(logging, e, "Error occured while sending the suiteData")


def sendTestcaseData(payload):

    try:
        response = _sendData(payload, DefaultSettings.urls["testcases"], method="POST")

        if response.status_code == 201:
            logging.info("data uploaded successfully")

    except Exception as e:
        common.errorHandler(logging, e, "Error occured while sending the testcaseData")


def _sendData(payload, url, method="POST"):

    response = requests.request(
        method=method,
        url=url,
        data=payload,
        headers=_getHeaders(),
    )
    response.raise_for_status()
    logging.debug(f"body: {payload}")
    logging.info(f"URL: {url}")
    logging.info(f"status: {response.status_code}")

    return response
