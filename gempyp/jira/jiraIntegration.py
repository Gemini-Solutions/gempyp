from gempyp.config import DefaultSettings
import requests
import json
import logging
import traceback
from datetime import datetime
from gempyp.engine import dataUpload


def createJira(jira_body, bridge_token, user_name):
    logging.info("----------- Trying to create Jira Ticket ------------")
    create_jira_api = DefaultSettings.urls["data"]["jira-api"]
    try:
        jira_res = dataUpload._sendData(jira_body, url=create_jira_api, bridge_token=bridge_token, user_name=user_name)
        if jira_res.status_code == 201 or jira_res.status_code == 200:
            jira_json = json.loads(jira_res.text)
            jira_id = jira_json["data"]["key"]
            print("jira created ------------------", jira_id)
            return jira_id
        else:
            logging.error("Unable to create the Jira")
    except Exception as e:
        traceback.format_exc()
        print(e)
        return None


def jiraIntegration(s_run_id, email, access_token, project_id, env, workflow, bridge_token, user_name, suiteName):
    logging.info("---------- In Jira Integration ---------")
    
    jira_id = None
    try:
        flow = workflow.strip("'").strip('"').split(",")
        flow = [str(i.strip(" ")) for i in flow]
    except Exception as e:
        print("ERROR: JIra workflow is can not be converted to proper format")
   
    jira_body = {
        "email": email, 
        "accessToken": access_token,
        "projectId": project_id, 
        "s_run_id": s_run_id,
        "flow": flow,
        "env": env,
        "accessToken": access_token,
        "suiteName": suiteName
    }
    jira_body = json.loads(json.dumps(str(jira_body).replace("'", '"')))
    try:
        logging.info("----------- Requesting JIRA API ------------")
        jira_id = createJira(jira_body, bridge_token, user_name)
        if jira_id:
            logging.info(f"----------- Jira Id - {jira_id} ------------")
        return jira_id
    except Exception as e:
        traceback.print_exc()
        return None
    