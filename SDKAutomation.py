import traceback
from gempyp.sdk.executor import Executor
from gempyp.libs.enums.status import status
import requests
import os
import json


def changeBridgeTokenFailed():
        obj=Executor()
        api = 'https://apis.gemecosystem.com/bridge/token/change'
        obj.reporter.addRow("Change Bridge Token API", "To Change bridge token of a user in our database.", status.INFO,method='-')
        obj.reporter.addRow("Validate the Changing Bridge Token API", api, status.INFO,method='-')
        try:
            jwt = os.getenv("jwt")
            
            response = requests.post(api, headers={"Authorization": "Bearer {}".format(jwt)},verify=False)
           
            if response.status_code == 200:
                res = json.loads(response.text)
                obj.reporter.addRow("Validate the message in Bridge Token", res["message"], status.FAIL, method="POST")
                obj.reporter.addRow("Validate the Change in Bridge Token", res["data"]["bridgeToken"], status.FAIL, method="POST")
                obj.reporter.addRow("Validate the Change in Bridge Token", "Response: {} ".format(res), status.FAIL, method="POST")
            elif response.status_code == 403:
                obj.reporter.addRow("Validate the Change in Bridge Token", "JWT expired, Bearer Token incorrect: {}".format(response.status_code),status.PASS, method="POST")
            else:
                obj.reporter.addRow("Validate the Bridge Token", "Bridge Token could nt be fetched: {}".format(response.status_code), status.FAIL, method="POST")
        except Exception as e:                  
            obj.reporter.addRow("Some Error while running the API", e, status.FAIL,method='-')

def changeBridgeTokenSuccess():
        obj1=Executor()
        api = 'https://apis.gemecosystem.com/bridge/token/change'
        obj1.reporter.addRow("Change Bridge Token API", "To Change bridge token of a user in our database.", status.INFO,method='-')
        obj1.reporter.addRow("Validate the Changing Bridge Token API", api, status.INFO,method='-')
        res1 = requests.post("https://apis.gemecosystem.com/login", json = {"username":"user759", "password": "e2fc714c4727ee9395f324cd2e7f331f"},verify=False)
        
        try:
            jwt = res1.json()["data"]["token"]
            response = requests.post(api, headers={"Authorization": "Bearer {}".format(jwt)},verify=False)
    
            if response.status_code == 200:
                res = json.loads(response.text)
                obj1.reporter.addRow("Validate the message in Bridge Token", res["message"], status.PASS, method="POST")
                obj1.reporter.addRow("Validate the Change in Bridge Token", res["data"]["bridgeToken"],status.PASS, method="POST")
                obj1.reporter.addRow("Validate the Change in Bridge Token", "Response: {} ".format(res),status.PASS, method="POST")
            elif response.status_code == 403:
                obj1.reporter.addRow("Validate the Change in Bridge Token", "Bearer Token incorrect: {}".format(response.status_code), status.FAIL, method="POST")
            else:
                obj1.reporter.addRow("Validate the Bridge Token", "Bridge Token could nt be fetched: {}".format(response.status_code), status.FAIL, method="POST")
        except Exception as e:                  
            obj1.reporter.addRow("Some Error while running the API", e, status.FAIL,method='-')


def fetchBridgeTokenFailed():
        obj2=Executor()
        api = 'https://apis.gemecosystem.com/bridge/token'
        obj2.reporter.addRow("Bridge Token API", "To fetch To fetch bridge token from our database.", status.INFO,method='-')
        obj2.reporter.addRow("Get Bridge Token API", api, status.INFO,method='-')
        try:
            jwt = "4a0bb70b-23fa-4801-b047-568a3fa059871656932464937"
            response = requests.get(api, headers={"Authorization": "Bearer {}".format(jwt)},verify=False)
           
            if response.status_code == 200:
                res = json.loads(response.text)
                obj2.reporter.addRow("Get the Bridge Token", "Bridge Token"+res["data"]["bridgeToken"], status.FAIL, method="GET")
                obj2.reporter.addRow("Get the Bridge Token", "Response: {}".format(res), status.FAIL, method="GET")
            elif response.status_code == 403:
                obj2.reporter.addRow("Get the Bridge Token", "JWT Expired. Bearer Token incorrect: {1} Response- {0}".format(response.text, response.status_code), status.PASS, method="GET")
            else:
                obj2.reporter.addRow("Get the Bridge Token", "Bridge Token could nt be fetched: {} Response- {}".format(response.status_code), status.FAIL, method="GET")
        except Exception as e:                  
            obj2.reporter.addRow("Some Error while running the API", e, status.FAIL,method='-')

def fetchBridgeTokenSuccess():
        obj3=Executor()
        api = 'https://apis.gemecosystem.com/bridge/token'
        obj3.reporter.addRow("Bridge Token API", "To fetch To fetch bridge token from our database.", status.INFO,method='-')
        obj3.reporter.addRow("Get Bridge Token API", api, status.INFO,method='-')
        res1 = requests.post("https://apis.gemecosystem.com/login", json = {"username":"arpit.mishra", "password": "263c66016009c2600783e167ef428c10"},verify=False)

        try:
            jwt = res1.json()["data"]["token"]
            response = requests.get(api, headers={"Authorization": "Bearer {}".format(jwt)},verify=False)
        
            if response.status_code == 200:
                res = json.loads(response.text)
                obj3.reporter.addRow("Get the Bridge Token", "Bridge Token"+res["data"]["bridgeToken"],status.PASS, method="GET")
                obj3.reporter.addRow("Get the Bridge Token", "Response: {}".format(res), status.PASS, method="GET")
            elif response.status_code == 403:
                obj3.reporter.addRow("Get the Bridge Token", "Bearer Token incorrect: {}".format(response.status_code), status.FAIL, method="GET")
            else:
                obj3.reporter.addRow("Get the Bridge Token", "Bridge Token could nt be fetched: {}".format(response.status_code), status.FAIL, method="GET")
        except Exception as e:                  
            obj3.reporter.addRow("Some Error while running the API", e, status.FAIL,method='-')

def companyName():
        obj4=Executor()
        api = "https://apis.gemecosystem.com/company"
        obj4.reporter.addRow("Company API", "To check if companies' name can be fetched or not", status.INFO,method='-')
        obj4.reporter.addRow("Validate the company API", api, status.INFO,method='-')
        
        try:
            response = requests.get(api, headers={"Content-Type": "application/json"},verify=False)
        
            if response.status_code == 200:
                obj4.reporter.addRow("Validate the company API", "SUCCESS, Status Code: {1}, RESPONSE: {0}".format(response.text,response.status_code), status.PASS, method="GET")
            else:
                obj4.reporter.addRow("Validate the company API", "Failed Status Code: {}".format(response.status_code), status.FAIL, method="GET")

        except Exception as e:
            obj4.reporter.addRow("Some Error while running the API", e, status.FAIL, method="GET")



if __name__ == "__main__":
    try:
        
        
        fetchBridgeTokenSuccess()
        changeBridgeTokenFailed()
        changeBridgeTokenSuccess()
        fetchBridgeTokenFailed()
        companyName()


    except Exception as e:
        traceback.print_exc()