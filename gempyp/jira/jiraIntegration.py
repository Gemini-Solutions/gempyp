from gempyp.config import DefaultSettings
import requests
import json
import logging
import traceback
from datetime import datetime


def closeJira(workflow):
    pass


def addComment(testcase_analytics, s_run_id, jira_id, email, access_token, jewel_link):
    comment_api = DefaultSettings.urls["data"]["comment-api"]
    comment_text = "Time: {} \nS_RUN_ID: {} \nJewel Link: {} \n".format(datetime.now().strftime("%Y-%b-%d"), s_run_id, jewel_link)
    for statuses in testcase_analytics.keys():
        comment_text += statuses + ":" +  str(testcase_analytics.get(statuses)) + "\n"
    body = {"email": email, "accessToken": access_token, "jiraId": jira_id, "comment": comment_text}
    try:
        comment_res = requests.post(comment_api, data=json.dumps(body), headers={"Content-Type": "application/json"})
        print(comment_res.status_code)
        if comment_res.status_code == 201 or comment_res.status_code == 200:
            return jira_id
        else:
            logging.error("Comment could not be added")
    except Exception as e:
        print(e)
        traceback.format_exc()
        return None


def createJira(s_run_id, testcase_analytics, jewel_link, email, access_token, title, project_id):
    logging.info("----------- Creating New Jira Ticket ------------")
    create_jira_api = DefaultSettings.urls["data"]["jira-api"]
    jira_body = {"email": email, "accessToken": access_token, "title": title, "projectId": project_id}
    try:
        jira_res = requests.post(create_jira_api, data=json.dumps(jira_body), headers={"Content-Type": "application/json"})
        print(jira_res)
        if jira_res.status_code == 201 or jira_res.status_code == 200:
            jira_json = json.loads(jira_res.text)
            jira_id = jira_json["data"]["key"]
            return jira_id
        else:
            logging.error("Unable to create the Jira")
    except Exception as e:
        traceback.format_exc()


def jiraIntegration(s_run_id, suite_status, testcase_analytics, jewel_link, email, access_token, title, project_id, workflow):
    logging.info("---------- In Jira Integration ---------")
    if suite_status.upper() == "PASS":
        closeJira(workflow)
    else:
        api = DefaultSettings.urls["data"]["last-five"]
        params = {"s_run_id": s_run_id}
        response = requests.get(api, params=params, headers={"Content-Type": "application/json"})
        prev_run_details = []
        if response.status_code == 200:
            prev_run_details = json.loads(response.text)
            if prev_run_details[0].get("Jira_id", None) is None:
                jira_id = createJira(s_run_id, testcase_analytics, jewel_link, email, access_token, title, project_id)
            elif prev_run_details[0]["Status"].upper() == "FAIL" or prev_run_details[0]["Status"].upper() == "ERR":
                logging.info("---------- Adding comment to the Jira Id {} -----------".format(prev_run_details[0]["Jira_id"]))
                jira_id = prev_run_details[0]["Jira_id"]
            elif prev_run_details[0]["Status"].upper() == "PASS" or prev_run_details[0]["Status"].upper() == "INFO":
                jira_id = createJira(s_run_id, testcase_analytics, jewel_link, email, access_token, title, project_id)
            jira_id = addComment(testcase_analytics, s_run_id, jira_id, email, access_token, jewel_link)
            return jira_id
        else:
            return None
