from gempyp.config import DefaultSettings
import json
import logging
import traceback
from gempyp.engine import dataUpload


def createAzureTicket(body, bridge_token, user_name):
    logging.info("----------- Trying to create Azure Ticket ------------")
    create_azure_api = DefaultSettings.urls["data"]["azure-api"]

    try:

        azure_res = dataUpload._sendData(body, url=create_azure_api, bridge_token=bridge_token, user_name=user_name)
        azure_json = json.loads(azure_res.text)
        logging.info(azure_json)

        if(azure_json.get("operation").upper() == "FAILURE"):
            logging.warn(azure_json.get("message"))
        try:
            return azure_json.get("data", None).get("key", None)
        except:
            logging.info("No need to create azure")            
            return None
        
    except Exception as e:
        traceback.format_exc()
        logging.info(e)
        return None


def azureIntegration(s_run_id, assigned_to, azure_pat, fields, project_name, env, workflow, azureTestcaseFlag, title, bridge_token, user_name, suiteName):  # adding title  ######################### post 1.0.4
    logging.info("---------- In Azure Integration ---------")
    
    azure_id = None
    if workflow:
        workflow = workflow.strip("'").strip('"').split(",")
        workflow = [str(i.strip(" ")) for i in workflow] 
   
    azure_body = {
        "assignedTo": assigned_to, 
        "pat": azure_pat,
        "project": project_name, 
        "s_run_id": s_run_id,
        "flow": workflow,
        "env": env,
        "suiteName": suiteName,
        "title": title,
        "fields": fields,
        "azureTestcaseFlag" : azureTestcaseFlag
    }  
    if not assigned_to:
        del azure_body["assignedTo"]
    if not workflow:
        del azure_body["flow"]
    if not title:
        del azure_body["title"]  
    if not fields:
        del azure_body["fields"]
        
    azure_body = json.loads(json.dumps(str(azure_body).replace("'", '"')))
    try:
        logging.info("----------- Requesting AZURE API ------------")
        azure_id = createAzureTicket(azure_body, bridge_token, user_name)
        if azure_id:
            logging.info(f"Azure Id - {azure_id}")
        return azure_id
    except Exception as e:
        traceback.print_exc()
        return None
    
