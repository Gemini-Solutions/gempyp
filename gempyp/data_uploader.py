import json
import ast
from gempyp.engine.testData import TestData
from gempyp.engine import dataUpload
import os
import logging
from cryptography.fernet import Fernet
from gempyp.config.DefaultSettings import encrypt_key, default_baseurl

# f = open(r'C:\Users\sachin.chand\gempyp_reports\GEMECO-API-PY_Beta_DV_FEATURES_2023_Apr_17_145953_097585\Unuploaded_data.json', 'r')

def dataUploader(file_path, bridge_token):
    # logging.INFO("******************************")
    f = open(file_path)
    encData = f.read()
    f.close()
    fernet = Fernet(encrypt_key)
    data = fernet.decrypt(encData).decode()
    data = ast.literal_eval(data)
    if bridge_token:
        data['bridge_token'] = bridge_token
    # if not data['base_url']:
    #     data['base_url'] = default_baseurl
    # print(data['base_url'])
    # response = dataUpload._sendData(" ",data['base_url'], data['bridge_token'], data['user_name'],"GET")
    # print(response.status_code)
    # if response.status_code == 200:
    #     url_enter_point = response.json()
    #     data["urls"]=url_enter_point["data"]    
    if 'suite_data' in data:
        obj = TestData()
        if len(data['suite_data']) > 1:
            payload = str(data['suite_data'][1])
        else:
            payload = str(data['suite_data'][0])
        response = dataUpload._sendData(payload, data['urls']['suite-exe-api'],data['bridge_token'], data['user_name'])
        if response.status_code == 201 or response.status_code == 200:
            logging.info('Suite Data is Uploaded Successfully')
            d = ast.literal_eval(data['suite_data'][0])
            s_run_id = d['s_run_id']
            print('Jewel Link',f"{data['urls']['jewel-url']}/#/autolytics/execution-report?s_run_id={s_run_id}")
            del data['suite_data']
        else:
            print('Suite data is not Uploaded')
    if 'testcases' in data:
        i = 0
        testcases_length = len(data['testcases'])
        while len(data['testcases'])>0 and i < testcases_length:
            response = dataUpload._sendData(data['testcases'][i], data['urls']['test-exe-api'],data['bridge_token'], data['user_name'])
            if response.status_code == 200 or response.status_code == 201:
                print("Testcase is uploaded successfully")
                del data['testcases'][i]
                testcases_length -= 1
            i += 1
            
    if 'suite_data' not in data and len(data['testcases']) == 0:
        os.remove(file_path)
    else:
        data = str(data)
        fernet = Fernet(encrypt_key)
        data = fernet.encrypt(data.encode())
        with open(file_path,'wb') as w:
            w.write(data)
        # data = json.loads(data)
    # else:
    #     print("Some Error From the Client Side, Maybe username or bridgeToken, Therefore terminating execution")
        