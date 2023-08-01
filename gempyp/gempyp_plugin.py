import pytest
import os
from gempyp.libs.common import *
from gempyp.engine.testData import TestData
from gempyp.libs.enums.status import status
from gempyp.engine.runner import getOutput
import tempfile
import inspect
from gempyp.common import common
import uuid




@pytest.fixture(scope='module')  # You can adjust the scope as needed
def reporter_common():
    return common.reporter

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
    if not config.option.gp_enable:
        return
    DATA = TestData()
    common.makeSuiteDetails()
    common.sendSuiteData()

def pytest_runtest_protocol(item, nextitem):
    # 'item' is the pytest Item object representing the current test case
    config = item.config
    if config.option.gp_enable:
        test_name = item.name
        common.getTestcaseData({"testcaseName":test_name})
    
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    config = item.config
    if config.option.gp_enable:
        outcome = yield
        rep = outcome.get_result()
        if rep.when=='call':
            source_code = inspect.getsource(item.obj)
            docstring=inspect.getdoc(item.obj)
            assertion_pattern = re.compile(r'\bassert\s+.*')
            assertion_statements = assertion_pattern.findall(source_code)
            if(docstring is not None):
                common.reporter.addRow("Additional information about Testcase", docstring, status.INFO)
            outcome_dict={('passed'):{'testcaseStatus':status.PASS,'description':str(assertion_statements)},('failed'):{'testcaseStatus':status.FAIL,'description':str(rep.longrepr)}}
            for teststep_status,mapping in outcome_dict.items():
                if(rep.outcome==teststep_status):
                        testcaseStatus=mapping['testcaseStatus']
                        description=mapping['description']
            common.reporter.addRow(rep.nodeid, description, testcaseStatus)
            common.send_testcase_data()
        if rep.outcome=='skipped':
            common.reporter.addRow(rep.nodeid, str(rep.longrepr), status.INFO)
            common.send_testcase_data()
    else:
         yield
         return

def pytest_sessionfinish(session):
    config = session.config
    if not config.option.gp_enable:
        return
    s_run_id = os.getenv("S_RUN_ID")
    file_path = os.path.join(tempfile.gettempdir(), s_run_id + ".txt")
    if os.path.exists(file_path):
                    with open(file_path, "r+") as f:
                        data = str(f.read())
                        common.createReport(json.loads(data))
                        jewelLink = DefaultSettings.getUrls('jewel-url')
                        if jewelLink is not None:
                            jewel_link = f'{jewelLink}/#/autolytics/execution-report?s_run_id={s_run_id}&p_id={DefaultSettings.project_id}'
                            print(f"Jewel link of gempyp report - {jewel_link}")







