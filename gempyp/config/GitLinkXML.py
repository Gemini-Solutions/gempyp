import requests
import os
import json
import logging
import tempfile
import uuid
from requests.auth import HTTPBasicAuth
from base64 import b64encode

def fetchFileFromGit(link,branch,username=None,bearer_token=None):  ################ post 1.0.4
        print("^^^^^^^^^^^^^^^^^^^^^")
        print(link)
        print(branch)
        list=link.split("/")
        api = f'https://api.github.com/repos/{list[3]}/{list[4]}/contents/{"/".join(list[7:])}?ref={branch}'
        try:
            print("$$$$$$$$$$$$$$$$$",api)
            # if(username is not None and token is not None):
            headers=None
            if bearer_token is not None:
                headers = {"Authorization": "Bearer {}".format(bearer_token)}
            elif username is not None and bearer_token is not None:
                headers = { 'Authorization' : basic_auth(username, bearer_token)}
            response = requests.get(api,headers=headers)
            # response=requests.get(api)
            json_response=json.loads(response.text)
            content_api=json_response["download_url"]
            response_content=requests.get(content_api)
            
            if(link.split(".")[-1]=="xml"):
                log_dir = str(os.path.join(tempfile.gettempdir(), 'XML'))
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                file = os.path.join(log_dir, 'XML_' + str(uuid.uuid4()) + '.xml')
                logging.info("GIT XML PATH"+str(file))
            else:
                file=os.path.join(tempfile.gettempdir(),link.split("/")[-1])
                logging.info("GIT FILE PATH"+str(file))
            print(file)
            with open(file, "w+") as f:
                f.write(response_content.text)
            logging.info("FILE IS DOWNLOADED")
            return file
        except Exception as e:                  
            logging.info("Some Error while running the API")

def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

if __name__ == "__main__":
    fetchFileFromGit("GIT:https://github.com/gem-sachinchand/addgitlink/blob/main/lakh1.csv:main:gem-sachinchand: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")