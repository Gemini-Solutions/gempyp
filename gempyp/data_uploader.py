import json
import ast
from gempyp.engine import dataUpload
import os
import logging
from cryptography.fernet import Fernet
from gempyp.config.DefaultSettings import encrypt_key, default_baseurl
import sys
import re

def dataUploader(file_path, bridge_token):
    
    # Reading the file sent by the user
    f = open(file_path)
    encData = f.read()
    f.close()
    #decryping the file here
    fernet = Fernet(encrypt_key)
    data = fernet.decrypt(encData).decode()
    data = ast.literal_eval(data)
    if bridge_token:
        data['bridge_token'] = bridge_token
    if not data['base_url']:
        data['base_url'] = default_baseurl
    print("Base Url Used:",data['base_url'])
    response = dataUpload._sendData(" ",data['base_url'], data['bridge_token'], data['user_name'],"GET")
    print("Calling Base Url",response.status_code)
    if response.status_code == 200:
        url_enter_point = response.json()
        data["urls"] = url_enter_point["data"]    
        if 'suite_data' in data:
            #trying to upload suite data 
            payload = str(data['suite_data'][-1])
            method = "POST"
            if len('suite_data') == 1:
                method = "PUT" 
            response = dataUpload._sendData(payload, data['urls']['suite-exe-api'],data['bridge_token'], data['user_name'], method)
            print("Suite data API Response")
            if response.status_code == 201 or response.status_code == 200:
                logging.info('Suite Data is Uploaded Successfully')
                d = ast.literal_eval(data['suite_data'][0])
                s_run_id = d['s_run_id']
                print('Jewel Link',f"{data['urls']['jewel-url']}/#/autolytics/execution-report?s_run_id={s_run_id}")
                del data['suite_data']
            else:
                print('Suite data is not Uploaded, therefore terminating the further execution')
                sys.exit()
        if 'testcases' in data:
            # trying to upload testcase
            i = -1
            loop_count = 1
            testcases_length = len(data['testcases'])
            while loop_count <= testcases_length:
                loop_count += 1
                response = dataUpload._sendData(data['testcases'][i], data['urls']['test-exe-api'],data['bridge_token'], data['user_name'])
                if response.status_code == 200 or response.status_code == 201:
                    print("Testcase is uploaded successfully")
                    del data['testcases'][i]
                            
        if 'suite_data' not in data and len(data['testcases']) == 0:
            #removing the file in case of all the testcase and suite data uploaded successfully
            print("Removing File")
            os.remove(file_path)
        else:
            # Rewriting the data in json file at same location
            print("Updating File")
            data = str(data)
            fernet = Fernet(encrypt_key)
            data = fernet.encrypt(data.encode())
            with open(file_path,'wb') as w:
                w.write(data)
            # data = json.loads(data)
    elif re.search('50[0-9]',str(response.status_code)):
            logging.info("Their is some problem on server side, Please try agai after sometime")
    else:
            logging.info("Some Error From the Client Side maybe Username or Bridgetoken, Therefore Terminating Execution")