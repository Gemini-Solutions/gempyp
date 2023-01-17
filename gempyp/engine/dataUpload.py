import traceback
import requests
import logging
from gempyp.config import DefaultSettings
from gempyp.libs.enums.status import status
import logging
import re
import json

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
            list_of_testcase = [s[:-37] for s in respon['data']['testcase_details']]
            return response._content
        else:
            return "failed"
    except Exception as e:
        traceback.print_exc()
        return "failed"

def sendSuiteData(payload, bridge_token, user_name, mode="POST"):
    """
    for checking the sendSuiteData api response
    """

    try:
        if len(respon) != 0:
            payload = dataAlter(payload)
        payload = noneRemover(payload)
        response = _sendData(payload, DefaultSettings.getUrls("suite-exe-api"), bridge_token, user_name, mode)

        if response and response.status_code == 201:
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
        else:
            logging.info("Suite data is not uploaded")
            if payload not in suite_data:
                suite_data.append(payload)
                
    except Exception as e:
        logging.error(traceback.format_exc())

def sendTestcaseData(payload, bridge_token, user_name):
    """
    for checking the sendTestCaseData api response
    """

    try:
        method = "POST"
        payload = json.loads(payload)
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
    logging.info(f"status: {response.status_code}")
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
    if respon['data']['testcase_info']:
        # adding the testcase analytics of both run
        payload['testcase_info'] = {i: payload['testcase_info'].get(i, 0) + respon['data']['testcase_info'].get(i, 0)
        for i in set(payload['testcase_info']).union(respon['data']['testcase_info'])}
        # updating the testcase analytics according to new run
        for key, value in stat.items():
            if key in payload['testcase_info']:
                payload['testcase_info'][key] += value
    
    # making testcase info in order
    prev_tc_count = 0
    try:
        prev_tc_count = sum(list(set(respon['data'].get('testcase_info', {}).values()) - set(['TOTAL'])))
    except Exception as e:
        print(e)

    #### to be improved, testcase info is incorrect, suite status is incorrect ##########    
    # prio_list = ['TOTAL', 'PASS', 'FAIL']
    # sorted_dict = {'TOTAL':0, 'PASS':0, 'FAIL':0}
    # sorted_dict = {}
    # for key in prio_list:
    #     if key in payload['testcase_info'] :
    #         sorted_dict[key] = payload['testcase_info'][key]
    #         if key == "PASS" or key == "FAIL":
    #             pass
    #         else:
    #             if sorted_dict[key] == 0:
    #                 sorted_dict.pop(key)
    #         payload['testcase_info'].pop(key)
    #     elif key == "PASS" or key == 'FAIL':
    #             sorted_dict[key] = 0                   ## useless

    sorted_dict = {'TOTAL':0, 'PASS':0, 'FAIL':0}
    sorted_dict.update(payload['testcase_info'])


    # status = "PASS"
    # if sorted_dict["PASS"] != sorted_dict["TOTAL"]:
    #     status = "FAIL"                                 ## useless
    payload['testcase_info'] = sorted_dict


    # payload['status'] = status
    #### to be improved, testcase info is incorrect, suite status is incorrect ########## 

    payload['expected_testcases'] += prev_tc_count  # respon['data']['expected_testcases']  ## incorrect
    # updating the suite status of according to new run
    # if payload['status'] != "PASS":
    #     pass
    # else:
    #     payload['status'] = respon['data']['status']

    # if old status = EXE, new status = EXE, incorrect logic                            ## incorrect

    for s in status:
        if sorted_dict.get(s.name, 0) > 0:
            payload['status'] = s.name  ## updated code to get correct status of the suite, based on the whole testcase info dict
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

