import requests
import logging
from gempyp.config import DefaultSettings
from gempyp.libs import common


def _getHeaders(bridgeToken):

    return {"Content-Type": "application/json", "bridgetoken": bridgeToken}



def sendSuiteData(payload, bridgeToken, mode="POST"):

    # print("---------suite payload \n", payload, "\n-----------")
    try:
        response = _sendData(payload, DefaultSettings.urls["suiteExec"], bridgeToken, mode)
        if response.status_code == 201:
            logging.info("data uploaded successfully")

    except Exception as e:
        common.errorHandler(logging, e, "Error occured while sending the suiteData")



def sendTestcaseData(payload, bridgeToken):

    # print("--------------- testcase payload\n", payload, "\n---------")
    try:
        response = _sendData(payload, DefaultSettings.urls["testcases"], bridgeToken, method="POST")

        if response.status_code == 201:
            logging.info("data uploaded successfully")

    except Exception as e:
        common.errorHandler(logging, e, "Error occured while sending the testcaseData")


def _sendData(payload, url, bridgeToken, method="POST"):

    response = requests.request(
        method=method,
        url=url,
        data=payload,
        headers=_getHeaders(bridgeToken),
    )
    logging.debug(f"body: {payload}")
    logging.info(f"URL: {url}")
    logging.info(f"status: {response.status_code}")
    response.raise_for_status()

    return response
