import json
import requests
import logging
import os
import sys
import traceback
# import urllib
from gempyp.config import DefaultSettings


# upload_file_api = DefaultSettings.getUrls('bucket-file-upload-api')
# upload_data_api = DefaultSettings.getUrls('bucket-data-upload-api')
# delete_file = DefaultSettings.getUrls('bucket-file-modify')

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
        try:
            api = DefaultSettings.getUrls('bucket-data-upload-api') if not api else api
            headers["Content-Type"] = "text/plain"
            params["file"] = file
            try:
                data = data.encode('utf-8')
            except Exception as e:
                print(e)
                traceback.print_exc()
            response = requests.post(api, params=params, data=data, headers=headers)
            data = json.loads(response.text)  
            print(response.text)  
            if response.status_code == 200:
                data = json.loads(response.text)    
                data_info = data["data"]
                return data_info
        except Exception as e:
            traceback.print_exc()
            print(e)
    elif file is not None:
        file = file.split(",")
        files = list()
        logging.info("---- Uploading file to s3 ----")
        api = DefaultSettings.getUrls('bucket-file-upload-api') if not api else api
        for f in file:
            if not os.path.isfile(f) or f == "N.A":
                logging.error("Path of file invalid - " + f)
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


def create_s3_link(**kwargs):
    """ creating s3 link to be viewed on file viewer on jewel UI"""

    s3_viewer = DefaultSettings.getUrls('file-viewer')
    if kwargs.get("url", None):
        params = "url=" + kwargs.get("url")
        kwargs.pop("url")
        for key, value in kwargs.items():
            params = f"{params}&{key}={value}"
        return f"{s3_viewer}?{params}"
    return None

if __name__ == "__main__":
    print(download_from_s3(api="https://apis-beta.gemecosystem.com/v1/download/file?id=gem-np:PYPRESTBEFOREFILE:BeforeAfterFile1.py",username="tanya.agarwal",bridge_token="374efe42-323e-4445-b89b-1ff750f000c61664541163883"))