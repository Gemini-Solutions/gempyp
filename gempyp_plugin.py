import pytest
import os
from gempyp.libs.common import *
from gempyp.engine.testData import TestData
from gempyp.libs.enums.status import status
from gempyp.engine.runner import getOutput
import tempfile
from gempyp.libs.enums.status import status
import inspect
from gempyp.common import Common


obj=Common()

def pytest_addoption(parser):
    """Add support for the RP-related options.

    :param parser: Object of the Parser class
    """
    group = parser.getgroup('reporting')

    def add_shared_option(name, help_str, default=None, action='store'):
        """
        Add an option to both the command line and the .ini file.

        This function modifies `parser` and `group` from the outer scope.

        :param name:     name of the option
        :param help_str: help message
        :param default:  default value
        :param action:   `group.addoption` action
        """
        parser.addini(
            name=name,
            default=default,
            help=help_str,
        )
        group.addoption(
            '--{0}'.format(name.replace('_', '-')),
            action=action,
            dest=name,
            help='{help} (overrides {name} config option)'.format(
                help=help_str,
                name=name,
            ),
        )

    group.addoption(
        '--gempyp-enable',
        action='store_true',
        dest='gp_enable',
        default=False,
        help='Enable gempyp plugin'
    )
    add_shared_option(
        name='project-name',
        help_str='project name',
        default='Pytest integration with gempyp',
    )
    add_shared_option(
        name='environment',
        help_str='environment name',
        default='PROD',
    )
    add_shared_option(
        name='jewel-user',
        help_str='jewel user',
        default=None,
    )
    add_shared_option(
        name='jewel-bridge-token',
        help_str='jewel_bridge_token',
        default=None,
    )
    add_shared_option(
        name='enter-point',
        help_str='End point',
        default=None,
    )
    add_shared_option(
        name='mail-to',
        help_str='mail-to',
        default=None,
    )
    add_shared_option(
        name='mail-cc',
        help_str='mail-cc',
        default=None,
    )
    add_shared_option(
        name='mail-bcc',
        help_str='mail-bcc',
        default=None,
    )
    add_shared_option(
        name='report-name',
        help_str='report-name',
        default='SMOKE_TEST',
    )
    add_shared_option(
        name='s-run-id',
        help_str='s-run-id',
        default=os.getenv("S_RUN_ID"),
    )
    add_shared_option(
        name='report-location',
        help_str='report-location',
        default=None,
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if config.option.gp_enable:
        DATA = TestData()
        obj.makeSuiteDetails()
        obj.sendSuiteData()
    
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call':
        obj.getTestcaseData({"testcaseName":rep.nodeid})
        source_code = inspect.getsource(item.obj)
        assertion_pattern = re.compile(r'\bassert\s+.*')
        assertion_statements = assertion_pattern.findall(source_code)
        if(rep.outcome=="passed"):
                testcaseStatus=status.PASS
                description=str(assertion_statements)
        elif(rep.outcome=="failed"):
                testcaseStatus=status.FAIL
                description=str(rep.longrepr)
        else:
                testcaseStatus=status.INFO
                description=str(assertion_statements)
        obj.reporter.addRow(rep.nodeid, description, testcaseStatus)
        obj.send_testcase_data()

def pytest_sessionfinish(session):
    s_run_id = os.getenv("S_RUN_ID")
    file_path = os.path.join(tempfile.gettempdir(), s_run_id + ".txt")
    if os.path.exists(file_path):
                    with open(file_path, "r+") as f:
                        data = str(f.read())
                        obj.createReport(json.loads(data))
                        jewelLink = DefaultSettings.getUrls('jewel-url')
                        if jewelLink is not None:
                            jewel_link = f'{jewelLink}/#/autolytics/execution-report?s_run_id={s_run_id}&p_id={DefaultSettings.project_id}'
                            print(f"Jewel link of gempyp report - {jewel_link}")
