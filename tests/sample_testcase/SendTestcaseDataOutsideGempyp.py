from asyncio.windows_events import NULL
from gempyp.config import DefaultSettings
import logging
import requests
import sys
import traceback
def sendData(testcaseJson,bridgeToken,username):
    try:
        if DefaultSettings.count > 3:
            logging.critical("Incorrect bridgetoken/username or APIs are down")
            sys.exit()
    
        response = requests.request(
            method="POST",
            url="https://apis.gemecosystem.com/testcase",
            data=testcaseJson,
            headers={"Content-Type": "application/json", "bridgetoken": bridgeToken, "username": username},
        )
        if response.status_code != 200 and response.status_code != 201:
            DefaultSettings.count+=1
        logging.info(f"status: {response.status_code}")
        response.raise_for_status()
        if response.status_code == 201:
            logging.info("data uploaded successfully")
    except Exception as e:
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    testcaseJson={"tc_run_id": "verify_testcase_9d9915a4-414e-4ce1-96d2-09ba886b99c5", "start_time": 1658818412926.537, "end_time": 1658818412928.585, "name": "verify_testcase", "category": "sample", "log_file": "logs\\verify_testcase_9d9915a4-414e-4ce1-96d2-09ba886b99c5.log", "status": "PASS", "steps": [{"title": "test", "description": "desc", "status": "PASS"}], "user": "tanya.agarwal", "machine": "GEMGN-220029", "result_file": NULL, "product_type": "GEMPYP", "ignore": False, "miscData": [], "s_run_id": "GEMPYP_TEST_PROD_9D9915A4-414E-4CE1-96D2-09BA886B99C5"}
    sendData(testcaseJson,"9d3d67c5-df92-4c2d-995f-10d71b0667bc1658310410707","tanya.agarwal")