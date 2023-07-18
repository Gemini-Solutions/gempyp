from gempyp.config import DefaultSettings
import requests
import json
import logging
import traceback
from datetime import datetime


def closeJira(workflow):
    pass


def addComment(testcase_info, s_run_id, jira_id, email, access_token, jewel_link):
    comment_api = DefaultSettings.urls["data"]["comment-api"]
    comment_text = ""
    if testcase_info["PASS"] == testcase_info["TOTAL"]:
        comment_text = "SUITE PASSED \n"
    comment_text += "Date: {} \nS_RUN_ID: {} \nJewel Link: {} \n".format(datetime.now().strftime("%Y-%b-%d"), s_run_id, jewel_link)
    for statuses in testcase_info.keys():
        comment_text += statuses + ":" +  str(testcase_info.get(statuses)) + "\n"
    body = {"email": email, "accessToken": access_token, "jiraId": jira_id, "comment": comment_text}
    try:
        comment_res = requests.post(comment_api, data=json.dumps(body), headers={"Content-Type": "application/json"})
        if comment_res.status_code == 201 or comment_res.status_code == 200:
            return jira_id
        else:
            logging.error("Comment could not be added")
    except Exception as e:
        logging.info(e)
        traceback.format_exc()
        return None


def createJira(email, access_token, title, project_id):
    logging.info("----------- Creating New Jira Ticket ------------")
    create_jira_api = DefaultSettings.urls["data"]["jira-api"]
    jira_body = {"email": email, "accessToken": access_token, "title": title, "projectId": project_id}
    try:
        jira_res = requests.post(create_jira_api, data=json.dumps(jira_body), headers={"Content-Type": "application/json"})
        if jira_res.status_code == 201 or jira_res.status_code == 200:
            jira_json = json.loads(jira_res.text)
            jira_id = jira_json["data"]["key"]
            return jira_id
        else:
            logging.error("Unable to create the Jira")
    except Exception as e:
        traceback.format_exc()
        logging.info(e)
        return None


def jiraIntegration(s_run_id, suite_status, testcase_info, jewel_link, email, access_token, project, project_id, title=None, workflow=None):
    logging.info("---------- In Jira Integration ---------")
    if title is None:
        title = project
    api = DefaultSettings.urls["data"]["last-five"]
    params = {"s_run_id": s_run_id}
    jira_id = None
    try:
        response = requests.get(api, params=params, headers={"Content-Type": "application/json"})
        prev_run_details = []
        if response.status_code == 200:
            prev_run_details = json.loads(response.text)
            jira_id = prev_run_details[0].get("Jira_id", None)
    except Exception as e:
        logging.info(e)
        return None
    if suite_status.upper() == "PASS" and prev_run_details[0]["Status"].upper() == "PASS":
        logging.info("----- \nCurrent suite_status is PASS and prev suite is also pass \nNo need to create jira \n------")
        return None
    elif suite_status.upper() == "PASS" and jira_id is not None and prev_run_details[0]["Status"].upper() not in ["PASS", "INFO"]:
        logging.info("----- Current suite_status is PASS ------")
        addComment(testcase_info, s_run_id, jira_id, email, access_token, jewel_link)
    elif suite_status.upper() == "FAIL" or suite_status.upper() == "ERR":
        try:
            if prev_run_details[0].get("Jira_id", None) is None:
                logging.info("------ Current suite_status is FAIL and no jira id for prev run ----")
                jira_id = createJira(email, access_token, title, project_id)
            elif prev_run_details[0]["Status"].upper() == "FAIL" or prev_run_details[0]["Status"].upper() == "ERR":
                logging.info("---------- Adding comment to the Jira Id {} -----------".format(prev_run_details[0]["Jira_id"]))
                jira_id = prev_run_details[0]["Jira_id"]
            elif prev_run_details[0]["Status"].upper() == "PASS" or prev_run_details[0]["Status"].upper() == "INFO":
                logging.info("----- Prev suite_status is PASS and current suite_status is FAIL or ERR -----")
                jira_id = createJira(email, access_token, title, project_id)
            jira_id = addComment(testcase_info, s_run_id, jira_id, email, access_token, jewel_link)
            return jira_id
        except Exception as e:
            logging.info(e)
            return None
        

