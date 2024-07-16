# from behave import before_scenario, 
# Feature-level Hooks
# @before.feature
import traceback
from gempyp.libs.enums.status import status
from gempyp.plugin.common import common
import time
# from gempyp.plugin.common import common.reporter

def before_feature(context, feature):
    scenario_count = len(feature.scenarios)
    suite_dict = {"expected-testcases":scenario_count}
    common.makeSuiteDetails(suite_dict)
    common.sendSuiteData()

def after_feature(context, feature):
    common.createReport()

def before_scenario(context, scenario):
    test = {"testcaseName":scenario.name}
    common.getTestcaseData(test)

# @after.scenario
def after_scenario(context, scenario):
    common.send_testcase_data()

# Step-level Hooks
# @before.step
def before_step(context, step):
    pass

# @after.step
def after_step(context, step):
    try:
        if str(step.status) == "Status.failed":
            common.reporter.addRow(step.name,step.keyword.strip(),common.reporter.Status.FAIL)
        elif str(step.status) == "Status.passed":
            common.reporter.addRow(step.name,step.keyword.strip(),common.reporter.Status.PASS)
        else:
            common.reporter.addRow(step.name,step.keyword.strip(),common.reporter.Status.ERR)
    except Exception:
        common.reporter.addRow(step.name,traceback.print_exc(),status.ERR)

