import json
import ast
from gempyp.engine import dataUpload
import os
import logging
from cryptography.fernet import Fernet
from gempyp.config.DefaultSettings import encrypt_key, default_baseurl
import sys
import re
import traceback
from gempyp.libs.gem_s3_common import upload_to_s3, create_s3_link
def dataUploader(file_path, bridge_token):

    try:
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
        if response.status_code == 200:
            url_enter_point = response.json()
            data["urls"] = url_enter_point["data"]  
            try:  
                if 'suite_data' in data:
                    data['suite_data'][-1] = ast.literal_eval(data['suite_data'][-1])
                    for i in range(len(data['suite_data'][-1]['meta_data'])):
                        if 'CONFIG_S3_URL' in data['suite_data'][-1]['meta_data'][i].keys():
                            xml_path = data['suite_data'][-1]['meta_data'][i]['CONFIG_S3_URL']
                            index = i
                            break
                    #trying to upload suite data 
                    if not re.search("^https://.", xml_path):
                        try:
                            xml_s3_url = upload_to_s3(data["urls"]["bucket-file-upload-api"], bridge_token=data['bridge_token'], username=data['user_name'], file=xml_path)[0]["Url"]
                            print("XML S3 URL", xml_s3_url)
                            data['suite_data'][-1]['meta_data'][i]['CONFIG_S3_URL'] = xml_s3_url
                        except Exception:
                            print('Some Problem Occured while uploading xml file on S3')
                    data['suite_data'][-1] = json.dumps(data['suite_data'][-1])
                    payload = str(data['suite_data'][-1])
                    method = "POST"
                    if len('suite_data') == 1:
                        method = "PUT" 
                    response = dataUpload._sendData(payload, data['urls']['suite-exe-api'],data['bridge_token'], data['user_name'], method)
                    print("Suite data API Response")
                    print(response.status_code)
                    if response.status_code == 201 or response.status_code == 200:
                        logging.info('Suite Data is Uploaded Successfully')
                        d = ast.literal_eval(data['suite_data'][0])
                        s_run_id = d['s_run_id']
                        print('Jewel Link',f"{data['urls']['jewel-url']}/#/autolytics/execution-report?s_run_id={s_run_id}")
                        del data['suite_data']
                    else:
                        print('Suite data is not Uploaded, therefore terminating the further execution')
                        sys.exit()
            except Exception:
                traceback.print_exc()
                sys.exit()
            try:       
                if 'testcases' in data:
                    # trying to upload testcase
                    i = -1
                    loop_count = 1
                    testcases_length = len(data['testcases'])
                    while loop_count <= testcases_length:
                        loop_count += 1
                        data['testcases'][i] = json.loads(data['testcases'][i])
                        if not re.search("^https://.", data['testcases'][i]['log_file']):
                            try:
                                print('Uploading Testcases Log File to S3')
                                s3_log_file_url = create_s3_link(url=upload_to_s3(data["urls"]["bucket-file-upload-api"], bridge_token=data['bridge_token'], username=data['user_name'], file=data['testcases'][i]['log_file'])[0]["Url"])
                                data['testcases'][i]['user_defined_data']['LOG_FILE'] = f'<a href="{s3_log_file_url}" target=_blank>view</a>'
                            except Exception:
                                print('some problem occured while uploading testcase log file')
                        if data['testcases'][i]['product_type'] == 'GEMPYP-DV':
                            if not re.search("^https://.", data['testcases'][i]['steps'][-1]["Attachment"][-1]):
                                print('Uploading DV Result File to S3')
                                s3_result_file_url = create_s3_link(url=upload_to_s3(data["urls"]["bucket-file-upload-api"], bridge_token=data.get('bridge_token',None), username=data.get('user_name',None), file=data['testcases'][i]['steps'][-1]["Attachment"][-1],tag="public")[0]["Url"]) 
                                s3_log_file_url = f'<a href="{s3_log_file_url}" target=_blank>view</a>'
                                data['testcases'][i]['steps'][-1]["Attachment"][-1] = s3_result_file_url
                        data['testcases'][i] = json.dumps(data['testcases'][i])    
                        response = dataUpload._sendData(data['testcases'][i], data['urls']['test-exe-api'],data['bridge_token'], data['user_name'])
                        if response.status_code == 200 or response.status_code == 201:
                            print("Testcase is uploaded successfully")
                            del data['testcases'][i]
            except Exception:
                traceback.print_exc()
                                
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
            print("There is some problem on server side, Please try again after sometime")
        else:
            print("Some Error From the Client Side maybe Username or Bridgetoken, Therefore Terminating Execution")
    except Exception:
        traceback.print_exc()