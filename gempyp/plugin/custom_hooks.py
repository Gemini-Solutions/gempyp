import traceback, os, argparse
from gempyp.libs.enums.status import status
from gempyp.plugin.common import common

total_scenario_count = 0

def countingScenarios(filePath):
    with open(filePath, 'r') as file:
        content = file.read()
        lines = content.splitlines()
        scenario_count = 0
        in_scenario_block = False
        for line in lines:
            line = line.strip()
            if line.startswith("Scenario"):
                in_scenario_block = True
                scenario_count += 1
            elif in_scenario_block and line.startswith("#"):
                # If we're in a scenario block and the line starts with '#', it's a commented scenario.
                scenario_count -= 1
            elif line == "":
                # Reset the flag when encountering an empty line to exit the scenario block.
                in_scenario_block = False
    return scenario_count


def before_all(context):
    # scenario_count = len(feature.scenarios)
    # suite_dict = {"expected-testcases":0}
    feature_directory = 'features'  # Change this to the directory where your feature files are located
    try:
        filePath = None
        parser = argparse.ArgumentParser()
        parser.add_argument('-filePath','-k',dest='filePath',type=str, required=False)
        args = parser.parse_args()
        config = vars(args)
        filePath = config.get('filePath',None)
    except Exception:
        print(traceback.print_exc())



    # Iterate through all feature files
    total_scenarios = 0
    if filePath:
        total_scenarios = countingScenarios(filePath)
    else:
        for root, dirs, files in os.walk(os.path.abspath(feature_directory)):
            for filename in files:
                if filename.endswith('.feature'):
                    filePath = os.path.join(root, filename)
                    total_scenarios += countingScenarios(filePath)
                    # Parse the feature file to count scenarios
                
    suite_dict = {"expected-testcases":total_scenarios}
    common.makeSuiteDetails(suite_dict)
    common.sendSuiteData()
    # before_feature(context, feature)

def after_all(context):
    common.createReport()
    

def before_scenario(context, scenario):
    test = {"testcaseName":scenario.name}
    common.getTestcaseData(test)


def after_scenario(context, scenario):
    feature_filename = context._runner.feature.filename
    common.reporter.addMisc("feature",feature_filename)
    common.send_testcase_data()


def after_step(context, step):

    txt_tb = u"".join(traceback.format_tb(step.exc_traceback))
    try:
        if str(step.status) == "Status.failed":
            common.reporter.addRow(step.name,str(step.exception).split('}')[0],common.reporter.Status.FAIL)
        elif str(step.status) == "Status.passed":
            common.reporter.addRow(step.name,step.keyword.strip(),common.reporter.Status.PASS)
        else:
            txt_tb = u"".join(traceback.format_tb(step.exc_traceback))
            common.reporter.addRow(step.name,str(step.exception).split('}')[0],common.reporter.Status.ERR)
    except Exception:
        common.reporter.addRow(step.name,traceback.print_exc(),status.ERR)


