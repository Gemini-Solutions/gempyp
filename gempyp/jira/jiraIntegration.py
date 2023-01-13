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
            try:
                return jira_json.get("data", None).get("key", None)
            except:
                logging.info("No need to create jira")            
                return None
        else:
            logging.info("Jira API Response - " + str(jira_res.text))
    except Exception as e:
        traceback.format_exc()
        logging.info(e)
        return None


def jiraIntegration(s_run_id, email, access_token, project_id, env, workflow, title, bridge_token, user_name, suiteName):  # adding title  ######################### post 1.0.4
    logging.info("---------- In Jira Integration ---------")
    
    jira_id = None
    if workflow:
        workflow = workflow.strip("'").strip('"').split(",")
        workflow = [str(i.strip(" ")) for i in workflow] 
   
    jira_body = {
        "email": email, 
        "accessToken": access_token,
        "projectId": project_id, 
        "s_run_id": s_run_id,
        "flow": workflow,
        "env": env,
        "suiteName": suiteName,
        "title": title
    }  # adding title  ######################### post 1.0.4
    if not workflow:
        del jira_body["flow"]
    if not title:
        del jira_body["title"]  # adding title  ######################### post 1.0.4
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
    
