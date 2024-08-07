import traceback
import requests
import logging
from gempyp.config import DefaultSettings
from gempyp.libs.enums.status import status
import logging
import re
import json
import sys

not_uploaded = []
suite_data = []
flag = False
suite_uploaded = False
list_of_testcase = []
respon = {}

# stat = {k.name: 0 for k in status}
# stat.update({"TOTAL":0})
stat= {**{k.name: 0 for k in status}, **{"TOTAL":0}}
def _getHeaders(bridge_token, user_name):
    """
    for getting the bridgeToken in _sendData method
    """
    return {"Content-Type": "application/json", "bridgeToken": bridge_token, "username": user_name}

def checkingData(run_id, bridge_token, user_name):
    try:
        url = DefaultSettings.getUrls("suite-exe-api") + "?s_run_id=" + run_id
        response = _sendData("", url , bridge_token, user_name, "GET")
        if response.status_code == 200:
            logging.info("Retrying to update and add testcases data present in DB")
            logging.info("Get Request successfull")
            global respon, suite_uploaded, list_of_testcase
            suite_uploaded = True
            respon = response.json()
            # list_of_testcase = [s[:-37] for s in respon['data']['testcase_details']]
            list_of_testcase = [s[:-37] for s in respon['data'].get('testcase_details', [])] if respon['data'].get('testcase_details', None) else []
            return response._content
        else:
            # return "failed"
            return False
    except Exception as e:
        traceback.print_exc()
        # return "failed"
        return False

def sendSuiteData(payload, bridge_token, user_name, mode="POST"):
    """
    for checking the sendSuiteData api response
    """

    try:
        if len(respon) != 0:
            payload = dataAlter(payload)
        payload = noneRemover(payload)
        response = _sendData(payload, DefaultSettings.getUrls("suite-exe-api"), bridge_token, user_name, mode)
        response_message = json.loads(response.text)["message"]
        autoKill = False
        if "New executions not allowed. Either enable AutoKill" in response_message:
            autoKill = True
        if response and response.status_code in [201, 200]:
            global suite_uploaded
            logging.info("Suite data uploaded successfully")
            suite_uploaded = True
            try:
                DefaultSettings.project_id = json.loads(response.text)["data"]["p_id"]
            except Exception as e:
                logging.info(traceback.format_exc())
            if payload in suite_data:
                suite_data.remove(payload)
        elif response and response.status_code == 200:
            logging.info("Suite Data updated Successfully")
        elif response.status_code and autoKill:
            logging.info("New executions not allowed. Either enable AutoKill or abort any previous incomplete executions before new suite runs.")
            sys.exit()
        elif re.search('50[0-9]',str(response.status_code)):
            logging.info("Suite data is not uploaded")
            if payload not in suite_data:
                suite_data.append(payload)
        # else:
        #     logging.info("Some Error From the Client Side, Terminating Execution")
        #     sys.exit()
        else:
            logging.info("Suite data is not uploaded")
            if payload not in suite_data:
                suite_data.append(payload)
        return response.status_code
    except Exception as e:
        logging.error(traceback.format_exc())

def sendTestcaseData(payload, bridge_token, user_name):
    """
    for checking the sendTestCaseData api response
    """
    try:
        method = "POST"
        payload = json.loads(payload)
        payload = attachmentRemover(payload)
        tc_run_id = payload["tc_run_id"]
        if tc_run_id[:-37] in list_of_testcase:
        #checking whether testcase present in previous run 
            payload, method = getTestcase(payload, method, bridge_token, user_name)
        payload = json.dumps(payload)
        response = _sendData(payload, DefaultSettings.getUrls("test-exe-api"), bridge_token, user_name, method)
        ### Applying regex to the response
        x = re.search("already present",response.text,re.IGNORECASE)
        if response.status_code == 201:
            logging.info("data uploaded successfully")
            if payload in not_uploaded:
                not_uploaded.remove(payload)
        elif response.status_code == 200:
            logging.info("data updated successfully")
            if payload in not_uploaded:
                not_uploaded.remove(payload)
    ### code for adding unuploaded testcases
        # elif re.search('50[0-9]',str(response.status_code)):
        #     if payload not in not_uploaded:
        #         not_uploaded.append(payload)
        #         logging.info("Testcase data is not uploaded")
        #         if x != None:
        #             global flag
        #             flag = True
        # else:
        #     logging.info("Some Error From the Client Side, Terminating Execution")
        #     sys.exit()
        elif response.status_code == 412:
            logging.info("Suite is killed on Jewel")
            return response.status_code
        else:
            if payload not in not_uploaded:
                not_uploaded.append(payload)
                logging.info("Testcase data is not uploaded")
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
    logging.info(f"Response text: {response.text}")
    logging.info(f"status: {response.status_code}")
    logging.info(f"Payload: {payload}")
    return response

def noneRemover(payload):
    data = json.loads(payload)
    for key,value in dict(data).items():
        if value == "-":
            del data[key]
    return json.dumps(data)

# code for changing suite data
def dataAlter(payload):
    payload = json.loads(payload)
    global respon, stat
    # changing start time
    payload['s_start_time'] = respon['data']['s_start_time']
    payload['testcase_info'] = {} if payload['testcase_info'] == "-" else payload['testcase_info']
    if respon['data'].get('testcase_info',None):
        # adding the testcase analytics of both run
        payload['testcase_info'] = {i: payload['testcase_info'].get(i, 0) + respon['data']['testcase_info'].get(i, 0)
        for i in set(payload['testcase_info']).union(respon['data']['testcase_info'])}
        # updating the testcase analytics according to new run
        for key, value in stat.items():
            if key in payload['testcase_info']:
                payload['testcase_info'][key] += value

    sorted_dict = {'TOTAL':0, 'PASS':0, 'FAIL':0}
    sorted_dict.update(payload['testcase_info'])
    payload['testcase_info'] = sorted_dict

    tc_count = 0
    try:
        # tc_count = sum(list(set(payload.get('testcase_info', {}).values()) - set(['TOTAL'])))
        tc_count = sum(payload.get('testcase_info', {}).values()) - payload.get('testcase_info', {}).get("TOTAL", 0)
    except Exception as e:
        traceback.print_exc()

    if tc_count > 0:
        payload['expected_testcases'] = tc_count
    for s in status:
        if sorted_dict.get(s.name, 0) > 0:
            payload['status'] = s.name
            break
    return  json.dumps(payload) 

# code for checking and updating testcase details
def getTestcase(payload, method, bridge_token, user_name):
    global flag

    for i in respon['data']['testcase_details']:

        if respon['data']['testcase_details'] and payload['tc_run_id'][:-37] in i:
            url = DefaultSettings.getUrls("test-exe-api") + "?tc_run_id=" + i
            response = _sendData(" ",url, bridge_token, user_name, "GET")
            if response.status_code == 200:
                logging.info("Testcase get request successfull")
                global flag
                flag = True
                if payload in not_uploaded:
                    not_uploaded.remove(payload)
            res = response.json()
            status = res['data']['status']
            stat[status] -= 1
            payload['tc_run_id'] = i
            stat["TOTAL"] -=1
            method = "PUT"
    return payload, method

def attachmentRemover(payload):
    data = payload.get("steps")
    for i in range(len(data)):
        for key,value in dict(data[i]).items():
            if value == "-":
                del data[i][key]
    payload['steps'] = data
    return payload
