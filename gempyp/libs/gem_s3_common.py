import json
import requests
import logging
import os, re
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
                data = str(data).encode('utf-8')
            except Exception as e:
                logging.warn(e)
                traceback.print_exc()
            response = requests.post(api, params=params, data=data, headers=headers)
            data = json.loads(response.text)  
            if response.status_code == 200:
                data = json.loads(response.text)    
                data_info = data["data"]
                return data_info
        except Exception as e:
            traceback.print_exc()
            logging.warn(e)
    elif file is not None:
        file = file.split(",")
        files = list()
        logging.info("---- Uploading file to s3 ----")
        api = DefaultSettings.getUrls('bucket-file-upload-api') if not api else api
        for f in file:
            if not os.path.isfile(f) or f == "N.A":
                logging.error("Path of file invalid - " + str(f))
                continue
            files.append(("file", (f.split("\\")[-1],open(f, "rb"),'text/xml')))
        response = requests.post(api, files=files, params=params, headers=headers) 
        data = json.loads(response.text) 
        if response.status_code == 200:
            data = json.loads(response.text)    
            file_info = data["data"]

            return file_info
        


def uploadToS3(api=None, tag=None, file=None, data=None, s_run_id=None, folder=None, username=None, bearer_token=None, bridge_token=None):

    print("*****************we are in upload to s3 function***************")
    
    """need to be make correct just dummy code"""
    logging.info("In Upload section")
    if bearer_token is not None:
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
    elif bridge_token is not None:
        if username is None:
            logging.ERROR("------ Please pass username along with Bridge token -----")
            sys.exit()
        headers = {"bridgeToken": bridge_token, "username": username, "Content-Type": "application/json"}
    body = {}
    if folder is not None:
        body["folder"] = folder
    if s_run_id is not None:
        body["s_run_id"] = s_run_id

    if type(file) == str:
        file = file.split(',')
    elif type(file) == list:
        pass
    else:
        logging.error("file data is inaccurate")
    filename = []
    for each in file:
        filename.append(os.path.basename(each))
    body["files"] = filename 
    body = json.dumps(body)
    response = requests.post(api, data=body, headers=headers)
    print(response.status_code)
    try:

        if response.status_code == 200:
            responseData = json.loads(response.text)
            resultData = responseData["data"]
            finalResult = []
            for each in file:
                filename = os.path.basename(each)
                j = None
                for i in range(len(resultData)):
                    j = i
                    files = []
                    if resultData[i].get(filename,None):
                        if not os.path.isfile(each):
                            logging.error("Path of file invalid - " + str(each))
                            continue
                        try:
                            files.append(("file", (os.path.basename(each),open(each, "rb"),'text/csv')))
                        except Exception:
                            print(traceback.print_exc())
                        api = resultData[i].get(os.path.basename(each),None)
                        response = requests.put(api, files=files, headers=headers)
                        if response.status_code == 200: ## this logic is needed to be modified currently support only one file at a time
                            # url = {}
                            # url["url"] = resultData[i].get("Url",None)
                            finalResult.append(resultData[i].get("Url",None))
                            # finalResult.append(url)
                        
                if j :
                    resultData.pop([j])
            return finalResult
        else:
            logging.warn("Some Error Ocurred While Uploading File to S3")
    except Exception:
            print(traceback.print_exc())
        
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
    return response


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
