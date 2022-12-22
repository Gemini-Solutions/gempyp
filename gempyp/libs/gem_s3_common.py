import json
import requests
import logging
import os
import sys


upload_file_api = "https://apis-beta.gemecosystem.com/v1/upload/file"
upload_data_api = "https://apis-beta.gemecosystem.com/v1/upload/data"
delete_file = "https://apis-beta.gemecosystem.com/v1/file/tag"

def upload_to_s3(api=None, tag=None, file=None, data=None, s_run_id=None, folder=None, username=None, bearer_token=None, bridge_token=None):
    logging.info("In Upload section")
    if bearer_token is not None:
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
    elif bridge_token is not None:
        if username is None:
            logging.ERROR("------ Please pass username along with Bridge token -----")
            sys.exit()
        headers = {"bridgeToken": bridge_token, "username": username}
    params = dict()
    if folder is not None:
        params["folder"] = folder
    if tag is not None: 
        params["tag"] = tag
    if s_run_id is not None:
        params["s_run_id"] = s_run_id
    if data is not None:
        logging.info("------ Uploading data to s3 -----")
        if api is None:
            api = "https://apis-beta.gemecosystem.com/v1/upload/data"
        headers["Content-Type"] = "text/plain"
        params["file"] = file
        response = requests.post(api, params=params, data=data, headers=headers)
        data = json.loads(response.text)    
        if response.status_code == 200:
            data = json.loads(response.text)    
            data_info = data["data"]
            print(data_info)
            return data_info
    elif file is not None:
        file = file.split(",")
        files = list()
        logging.info("---- Uploading file to s3 ----")
        if api is None:
            api = "https://apis-beta.gemecosystem.com/v1/upload/file"
        for f in file:
            if not os.path.isfile(f):
                logging.error("Path of file invalid - ", f)
                continue
            files.append(("file", open(f, "rb")))
        response = requests.post(api, files=files, params=params, headers=headers)  
        data = json.loads(response.text)    
        if response.status_code == 200:
            data = json.loads(response.text)    
            file_info = data["data"]
            return file_info

def download_from_s3(api, bearer_token=None, bridge_token=None, username=None, id=None):
    logging.info("In Download section")
    if bearer_token is not None:
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
    elif bridge_token is not None:
        if username is None:
            logging.ERROR("------ Please pass username along with Bridge token -----")
            sys.exit()
        headers = {"bridgeToken": bridge_token, "username": username}
    params = dict()
    if '?' not in api and id is None:
        logging.error("Please pass download url or the id")
        sys.exit()
    elif '?' in api:
        api_query = api.split('?')
        params = api_query[1][3:]
        api = api_query[0]
        params = {"id": "{}".format(params)}
    elif '?' not in api and id is not None:
        params = {"id": id}
    response = requests.get(api, params=params, headers=headers)  
    return response.text


if __name__ == "__main__":
    print(download_from_s3(bridge_token="9998284c-b61e-45d1-accd-2ce7d6f8f0a81670592834097"))