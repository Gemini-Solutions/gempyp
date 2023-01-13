import requests
import os
import json
import logging
import tempfile
import uuid
from requests.auth import HTTPBasicAuth

def fetchBridgeToken(link,branch,username,token):   #  ######################## post 1.0.4
        list=link.split("/")
        api = f'https://api.github.com/repos/{list[3]}/{list[4]}/contents/{"/".join(list[7:])}?ref={branch}'
        try:
            response = requests.get(api,auth = HTTPBasicAuth(username, token))
            json_response=json.loads(response.text)
            content_api=json_response["download_url"]
            response_content=requests.get(content_api)
            log_dir = str(os.path.join(tempfile.gettempdir(), 'XML'))
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            suiteLogsLoc = os.path.join(log_dir, 'XML_' + str(uuid.uuid4()) + '.xml')
            print(response_content.text)
            with open(suiteLogsLoc, "w+") as f:
                f.write(response_content.text)
            return suiteLogsLoc
        except Exception as e:                  
            logging.info("Some Error while running the API")

if __name__ == "__main__":
    fetchBridgeToken("GIT:https://github.com/Gemini-Solutions/gempyp/blob/dev/tests/configTest/Gempyp_Test_suite.xml:dev:username:token")